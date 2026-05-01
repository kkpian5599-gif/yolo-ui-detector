#!/bin/bash
# ══════════════════════════════════════════════════════════════
#  YOLO UI 检测器 — 云端训练脚本 v2
#  硬件: RTX 3090 24G / 16核CPU / 32G内存
# ══════════════════════════════════════════════════════════════
#
#  用法示例:
#    bash auto_train.sh                          # 全量训练（默认5000张/150轮）
#    bash auto_train.sh --finetune best.pt       # 增量微调（从已有模型继续，30轮）
#    bash auto_train.sh --count 2000 --epochs 80 # 自定义数量/轮数
#    bash auto_train.sh --clean-dataset          # 训练前清空旧数据集
#    bash auto_train.sh --skip-smoke             # 跳过烟雾测试
#    bash auto_train.sh --finetune best.pt --count 1000 --epochs 50 --clean-dataset
#
# ══════════════════════════════════════════════════════════════

set -euo pipefail

# ─── 默认参数 ─────────────────────────────────────────────────
COUNT=5000
EPOCHS=150
BASE_MODEL="yolo11m.pt"   # 全量训练起点
FINETUNE_MODEL=""         # 不为空则走增量微调模式
IMGSZ=640
BATCH=48
WORKERS=8
DEVICE=0
NAME="yolo_ui"
SKIP_SMOKE=false
CLEAN_DATASET=false

SMOKE_COUNT=5
SMOKE_EPOCHS=2

# ─── 解析命令行 ───────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --count)         COUNT="$2";           shift 2 ;;
        --epochs)        EPOCHS="$2";          shift 2 ;;
        --model)         BASE_MODEL="$2";      shift 2 ;;
        --finetune)      FINETUNE_MODEL="$2";  shift 2 ;;
        --imgsz)         IMGSZ="$2";           shift 2 ;;
        --batch)         BATCH="$2";           shift 2 ;;
        --workers)       WORKERS="$2";         shift 2 ;;
        --device)        DEVICE="$2";          shift 2 ;;
        --name)          NAME="$2";            shift 2 ;;
        --skip-smoke)    SKIP_SMOKE=true;      shift   ;;
        --clean-dataset) CLEAN_DATASET=true;   shift   ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

# ─── 模式判断 ─────────────────────────────────────────────────
if [ -n "$FINETUNE_MODEL" ]; then
    MODE="finetune"
    START_MODEL="$FINETUNE_MODEL"
    # 增量微调推荐参数（如用户没有自定义则覆盖默认值）
    [ "$COUNT"  -eq 5000 ] && COUNT=1000
    [ "$EPOCHS" -eq 150  ] && EPOCHS=50
else
    MODE="full"
    START_MODEL="$BASE_MODEL"
fi

# ─── 工具函数 ─────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

SCRIPT_START=$(date +%s)
STEP_START=$SCRIPT_START

elapsed_since() {
    local diff=$(( $(date +%s) - $1 ))
    printf "%dh%02dm%02ds" $((diff/3600)) $(( (diff%3600)/60 )) $((diff%60))
}
total_elapsed() { elapsed_since "$SCRIPT_START"; }
step_elapsed()  { elapsed_since "$STEP_START";  }
step_cost()     {
    local secs=$(( $(date +%s) - $1 ))
    awk "BEGIN { printf 'CNY %.3f', $secs/3600*1.06 }"
}
log()  { echo ""; echo "[$(date '+%H:%M:%S') | 已用 $(total_elapsed)] $*"; }
sep()  { echo ""; echo "══════════════════════════════════════════════════"; }
ok()   { echo "  ✔  $*"; }
info() { echo "  ·  $*"; }
begin_step() { STEP_START=$(date +%s); echo "  ⏱  步骤开始: $(date '+%Y-%m-%d %H:%M:%S')"; }

# ─── 启动横幅 ─────────────────────────────────────────────────
sep
log "🚀 YOLO UI 训练脚本 v2 启动"
echo ""
echo "  模式:      $MODE"
echo "  起点模型:  $START_MODEL"
echo "  生成数量:  $COUNT 张"
echo "  训练轮数:  $EPOCHS epochs"
echo "  Batch:     $BATCH  |  Workers: $WORKERS  |  Device: $DEVICE"
echo "  清空数据:  $CLEAN_DATASET"
echo "  跳烟雾:    $SKIP_SMOKE"
echo ""

# ══════════════════════════════════════════════════════════════
# STEP 0 — 安装依赖
# ══════════════════════════════════════════════════════════════
sep; log "STEP 0 / 5 — 安装依赖"
begin_step
pip install ultralytics Pillow playwright -q
playwright install chromium
ok "依赖安装完成 ($(step_elapsed))"

# ══════════════════════════════════════════════════════════════
# STEP 1 — 烟雾测试（可跳过）
# ══════════════════════════════════════════════════════════════
if [ "$SKIP_SMOKE" = false ]; then
    sep; log "STEP 1 / 5 — Smoke Test (${SMOKE_COUNT} 张 / ${SMOKE_EPOCHS} epoch)"
    echo "  目的: 验证完整流程无报错，避免正式跑到一半才崩"
    begin_step

    rm -rf dataset_smoke

    python -m generator.main \
        --count "$SMOKE_COUNT" \
        --start 0 \
        --output-dir dataset_smoke

    yolo detect train \
        model="$START_MODEL" \
        data=dataset_smoke/data.yaml \
        epochs="$SMOKE_EPOCHS" \
        imgsz="$IMGSZ" \
        batch="$BATCH" \
        workers="$WORKERS" \
        device="$DEVICE" \
        name="${NAME}_smoke" \
        exist_ok=True \
        verbose=False

    # YOLO detect 训练结果在 runs/detect/{name}/ 下
    SMOKE_DIR=$(find runs/detect -maxdepth 1 -type d -name "${NAME}_smoke" 2>/dev/null | head -1)
    rm -rf dataset_smoke "$SMOKE_DIR"

    ok "Smoke Test 通过！($(step_elapsed))"
else
    log "STEP 1 跳过 (--skip-smoke)"
fi

# ══════════════════════════════════════════════════════════════
# STEP 2 — 生成数据集
# ══════════════════════════════════════════════════════════════
sep; log "STEP 2 / 5 — 生成数据集 (${COUNT} 张)"
begin_step

# 清空旧数据（可选）
if [ "$CLEAN_DATASET" = true ]; then
    info "清空旧数据集 dataset/ ..."
    rm -rf dataset
    ok "旧数据已清空"
fi

python -m generator.main --count "$COUNT"

N_TRAIN=$(find dataset/images/train -name "*.jpg" 2>/dev/null | wc -l)
N_VAL=$(find   dataset/images/val   -name "*.jpg" 2>/dev/null | wc -l)
ok "数据集生成完毕: ${N_TRAIN} train / ${N_VAL} val ($(step_elapsed))"

# ══════════════════════════════════════════════════════════════
# STEP 3 — 训练
# ══════════════════════════════════════════════════════════════
sep; log "STEP 3 / 5 — YOLOv11 训练"
echo ""
info "起点模型:  $START_MODEL"
info "数据集:    dataset/data.yaml"
info "Epochs:    $EPOCHS"
info "模式:      $MODE"
echo ""
begin_step

if [ "$MODE" = "finetune" ]; then
    # ── 增量微调：低学习率，避免遗忘旧知识 ──
    yolo detect train \
        model="$START_MODEL" \
        data=dataset/data.yaml \
        epochs="$EPOCHS" \
        imgsz="$IMGSZ" \
        batch="$BATCH" \
        workers="$WORKERS" \
        device="$DEVICE" \
        name="$NAME" \
        exist_ok=True \
        lr0=0.0001 \
        lrf=0.01 \
        warmup_epochs=1 \
        cos_lr=True \
        label_smoothing=0.05 \
        optimizer=AdamW
else
    # ── 全量训练：标准配置 ──
    yolo detect train \
        model="$START_MODEL" \
        data=dataset/data.yaml \
        epochs="$EPOCHS" \
        imgsz="$IMGSZ" \
        batch="$BATCH" \
        workers="$WORKERS" \
        device="$DEVICE" \
        name="$NAME" \
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
        translate=0.1 \
        scale=0.5 \
        fliplr=0.5 \
        mosaic=0.8 \
        mixup=0.1
fi

TRAIN_COST=$(step_cost $STEP_START)
ok "训练完成 ($(step_elapsed)，约 $TRAIN_COST)"

# ─── 自动定位 best.pt（避免 YOLO 路径嵌套问题）───────────────
BEST_PT=$(find runs -name "best.pt" -path "*/${NAME}/weights/best.pt" | head -1)
if [ -z "$BEST_PT" ]; then
    BEST_PT=$(find runs -name "best.pt" | grep -v smoke | sort | tail -1)
fi
if [ -z "$BEST_PT" ]; then
    echo ""
    echo "  ✘ 找不到 best.pt，训练可能失败，请检查 runs/ 目录"
    exit 1
fi
TRAIN_DIR="$(dirname "$(dirname "$BEST_PT")")"   # runs/.../yolo_ui
ok "模型路径: $BEST_PT"

# ══════════════════════════════════════════════════════════════
# STEP 4 — 导出 ONNX
# ══════════════════════════════════════════════════════════════
sep; log "STEP 4 / 5 — 导出 ONNX"
begin_step

yolo export \
    model="$BEST_PT" \
    format=onnx \
    imgsz="$IMGSZ" \
    simplify=True

BEST_ONNX="${BEST_PT%.pt}.onnx"
ok "ONNX 导出完成: $BEST_ONNX ($(step_elapsed))"

# ══════════════════════════════════════════════════════════════
# STEP 5 — 验证集评估
# ══════════════════════════════════════════════════════════════
sep; log "STEP 5 / 5 — 验证集评估"
begin_step

yolo val \
    model="$BEST_PT" \
    data=dataset/data.yaml \
    imgsz="$IMGSZ" \
    batch=16 \
    device="$DEVICE" \
    name="${NAME}_val" \
    exist_ok=True \
    || log "⚠  val 步骤失败（不影响模型）"

ok "验证完成 ($(step_elapsed))"

# ══════════════════════════════════════════════════════════════
# 完成汇总
# ══════════════════════════════════════════════════════════════
TOTAL_SECS=$(( $(date +%s) - SCRIPT_START ))
TOTAL_H=$((TOTAL_SECS/3600))
TOTAL_M=$(( (TOTAL_SECS%3600)/60 ))
TOTAL_S=$((TOTAL_SECS%60))
TOTAL_COST=$(awk "BEGIN { printf '%.3f', $TOTAL_SECS/3600*1.06 }")

sep
log "🎉 全部完成！"
echo ""
echo "  ┌─────────────────────────────────────────────────┐"
printf "  │  模式:      %-35s│\n" "$MODE"
printf "  │  总耗时:    %dh %02dm %02ds%27s│\n" $TOTAL_H $TOTAL_M $TOTAL_S ""
printf "  │  估算费用:  CNY %-32s│\n" "$TOTAL_COST (按 1.06/h)"
echo  "  ├─────────────────────────────────────────────────┤"
printf "  │  模型 .pt:  %-35s│\n" "$BEST_PT"
printf "  │  模型 ONNX: %-35s│\n" "$BEST_ONNX"
printf "  │  训练日志:  %-35s│\n" "$TRAIN_DIR/results.csv"
echo  "  └─────────────────────────────────────────────────┘"
echo ""
echo "  打包下载命令:"
echo "  tar -czf yolo_ui_$(date +%Y%m%d_%H%M).tar.gz $TRAIN_DIR/"
echo ""
