#!/bin/bash
# 云端一键脚本：[Smoke Test] → 生成数据 → 训练 YOLOv11 → 导出 ONNX
# 硬件: RTX 3090 24G / 16核CPU / 32G内存
#
# 用法:
#   bash auto_train.sh                        # 完整流程（烟雾测试通过后自动继续）
#   bash auto_train.sh --skip-smoke           # 跳过烟雾测试，直接正式跑
#   bash auto_train.sh --count 2000 --epochs 150
#   bash auto_train.sh --batch 64 --device 0

set -e

# ── 参数默认值（RTX 3090 24G 优化配置）─────────────────
COUNT=5000          # 正式生成图片数量（RTX 3090 24G 高质量生产配置）
EPOCHS=150          # 训练轮数（5000张数据推荐150轮充分收敛）
MODEL="yolo11m.pt"  # 中型模型，3090 24G 完全驾驭
IMGSZ=640           # 图像尺寸
BATCH=48            # 3090 24G 显存，batch=48 安全上限（可试64）
WORKERS=8           # 16核CPU，dataloader 用8线程
DEVICE=0            # GPU 0
NAME="yolo_ui"
SKIP_SMOKE=false    # 是否跳过烟雾测试

SMOKE_COUNT=5       # 烟雾测试生成图片数
SMOKE_EPOCHS=2      # 烟雾测试训练轮数

# ── 解析命令行 ─────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --count)       COUNT="$2";       shift 2 ;;
        --epochs)      EPOCHS="$2";      shift 2 ;;
        --model)       MODEL="$2";       shift 2 ;;
        --imgsz)       IMGSZ="$2";       shift 2 ;;
        --batch)       BATCH="$2";       shift 2 ;;
        --workers)     WORKERS="$2";     shift 2 ;;
        --device)      DEVICE="$2";      shift 2 ;;
        --name)        NAME="$2";        shift 2 ;;
        --skip-smoke)  SKIP_SMOKE=true;  shift   ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# ── 时间工具函数 ───────────────────────────────────────────
SCRIPT_START=$(date +%s)          # 脚本启动时间（unix 秒）
STEP_START=$SCRIPT_START          # 当前步骤开始时间

elapsed_since() {
    # 返回从指定时间点到现在经过了多少 H:M:S
    local t0=$1
    local diff=$(( $(date +%s) - t0 ))
    printf "%dh%02dm%02ds" $((diff/3600)) $(( (diff%3600)/60 )) $((diff%60))
}

total_elapsed() { elapsed_since "$SCRIPT_START"; }

step_elapsed() { elapsed_since "$STEP_START"; }

step_cost() {
    # 按 ¥1.06/小时 估算当前步骤费用
    local t0=$1
    local secs=$(( $(date +%s) - t0 ))
    awk "BEGIN { printf '¥%.3f', $secs/3600*1.06 }"
}

log() {
    echo ""
    echo "[$(date '+%H:%M:%S') | 已用 $(total_elapsed)] $*"
}
sep() { echo ""; echo "══════════════════════════════════════════════════"; }

begin_step() {
    # 记录步骤开始时间并打印
    STEP_START=$(date +%s)
    echo "  ⏱  步骤开始: $(date '+%Y-%m-%d %H:%M:%S')"
}

sep
log "🚀 YOLO UI 训练脚本启动"
echo "  开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  配置: COUNT=$COUNT | EPOCHS=$EPOCHS | MODEL=$MODEL | BATCH=$BATCH"
echo ""

# ──────────────────────────────────────────────────────
# STEP 0 — 安装依赖
# ──────────────────────────────────────────────────────
sep; log "STEP 0 / 5 — 安装依赖"
begin_step
pip install ultralytics Pillow playwright -q
playwright install chromium
log "依赖安装完成（耗时 $(step_elapsed)）"

# ──────────────────────────────────────────────────────
# STEP 1 — 烟雾测试
# ──────────────────────────────────────────────────────
if [ "$SKIP_SMOKE" = false ]; then
    sep; log "STEP 1 / 5 — Smoke Test（${SMOKE_COUNT} 张图 / ${SMOKE_EPOCHS} epoch）"
    echo "  目的：验证完整流程无报错，不跑真实训练"
    echo ""
    begin_step

    # 清空旧烟雾测试数据
    rm -rf dataset_smoke

    # 生成 5 张测试图到独立 smoke 目录，避免覆盖或碰撞正式 dataset
    python -m generator.main --count "$SMOKE_COUNT" --start 0 --output-dir dataset_smoke

    log "Smoke Test — 开始训练 ${SMOKE_EPOCHS} epoch..."
    yolo detect train \
        model="$MODEL" \
        data=dataset_smoke/data.yaml \
        epochs="$SMOKE_EPOCHS" \
        imgsz="$IMGSZ" \
        batch="$BATCH" \
        workers="$WORKERS" \
        device="$DEVICE" \
        name="${NAME}_smoke" \
        project=runs \
        exist_ok=True \
        verbose=False

    # 清理烟雾测试产物
    rm -rf dataset_smoke runs/${NAME}_smoke

    log "✅ Smoke Test 通过！耗时 $(step_elapsed)，开始正式生成+训练..."
else
    log "STEP 1 跳过（--skip-smoke）"
fi

# ──────────────────────────────────────────────────────
# STEP 2 — 正式生成数据
# ──────────────────────────────────────────────────────
sep; log "STEP 2 / 5 — 正式生成数据集（${COUNT} 张）"
echo "  配置: train/val 自动分割 (85%/15%)"
echo "  分辨率: 桌面 + 移动端混合"
echo ""
begin_step

python -m generator.main --count "$COUNT"

N_TRAIN=$(find dataset/images/train -name "*.jpg" 2>/dev/null | wc -l)
N_VAL=$(find dataset/images/val   -name "*.jpg" 2>/dev/null | wc -l)
log "数据集生成完毕: ${N_TRAIN} train / ${N_VAL} val（耗时 $(step_elapsed)）"

# ──────────────────────────────────────────────────────
# STEP 3 — 正式训练
# ──────────────────────────────────────────────────────
sep
log "STEP 3 / 5 — YOLOv11 训练"
echo ""
echo "  模型:    $MODEL"
echo "  数据:    dataset/data.yaml"
echo "  Epochs:  $EPOCHS"
echo "  ImgSz:   $IMGSZ"
echo "  Batch:   $BATCH  (RTX 3090 24G 优化)"
echo "  Workers: $WORKERS"
echo "  Device:  $DEVICE"
echo ""
begin_step

yolo detect train \
    model="$MODEL" \
    data=dataset/data.yaml \
    epochs="$EPOCHS" \
    imgsz="$IMGSZ" \
    batch="$BATCH" \
    workers="$WORKERS" \
    device="$DEVICE" \
    name="$NAME" \
    project=runs \
    exist_ok=True \
    optimizer=AdamW \
    lr0=0.001 \
    lrf=0.01 \
    warmup_epochs=3 \
    cos_lr=True \
    label_smoothing=0.1 \
    hsv_h=0.015 \
    hsv_s=0.7 \
    hsv_v=0.4 \
    degrees=0 \
    translate=0.1 \
    scale=0.5 \
    flipud=0.0 \
    fliplr=0.5 \
    mosaic=0.8 \
    mixup=0.1

log "✅ 训练完成（耗时 $(step_elapsed)，约 $(step_cost $STEP_START)）"

# ──────────────────────────────────────────────────────
# STEP 4 — 导出 ONNX
# ──────────────────────────────────────────────────────
sep; log "STEP 4 / 5 — 导出 ONNX"
begin_step
yolo export \
    model="runs/detect/${NAME}/weights/best.pt" \
    format=onnx \
    imgsz="$IMGSZ" \
    simplify=True

log "ONNX 导出完成（耗时 $(step_elapsed)）"

# ──────────────────────────────────────────────────────
# STEP 5 — 自动验证（P4：训练完输出 mAP 指标）
# ──────────────────────────────────────────────────────
sep; log "STEP 5 / 5 — 验证集评估（输出 mAP）"
begin_step
yolo val \
    model="runs/detect/${NAME}/weights/best.pt" \
    data=dataset/data.yaml \
    imgsz="$IMGSZ" \
    batch=16 \
    device="$DEVICE" \
    name="${NAME}_val" \
    project=runs \
    exist_ok=True || log "⚠️  val 步骤失败（不影响模型）"

log "验证完成（耗时 $(step_elapsed)）"

# ─────────────────── 最终汇总 ────────────────────────────
TOTAL_SECS=$(( $(date +%s) - SCRIPT_START ))
TOTAL_H=$((TOTAL_SECS/3600))
TOTAL_M=$(( (TOTAL_SECS%3600)/60 ))
TOTAL_S=$((TOTAL_SECS%60))
TOTAL_COST=$(awk "BEGIN { printf '%.3f', $TOTAL_SECS/3600*1.06 }")

sep
log "🎉 全部完成！"
echo ""
echo "  ┌─────────────────────────────────────────┐"
echo "  │  开始时间:  $(date -d @$SCRIPT_START '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r $SCRIPT_START '+%Y-%m-%d %H:%M:%S')  │"
echo "  │  结束时间:  $(date '+%Y-%m-%d %H:%M:%S')              │"
printf "  │  总耗时:    %dh %02dm %02ds                     │\n" $TOTAL_H $TOTAL_M $TOTAL_S
printf "  │  估算费用:  ¥%s (按 ¥1.06/h)          │\n" "$TOTAL_COST"
echo "  └─────────────────────────────────────────┘"
echo ""
echo "  模型权重:  runs/detect/${NAME}/weights/best.pt"
echo "  ONNX:      runs/detect/${NAME}/weights/best.onnx"
echo "  训练曲线:  runs/detect/${NAME}/results.csv"
echo "  验证结果:  runs/detect/${NAME}_val/"
echo ""
