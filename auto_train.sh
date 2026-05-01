#!/bin/bash
# 云端一键脚本：生成数据 → 训练 YOLOv11 → 导出 ONNX
# 用法:
#   bash auto_train.sh                        # 默认 500 张、60 epoch
#   bash auto_train.sh --count 2000 --epochs 100 --batch 32 --device 0

set -e  # 任何步骤出错立即停止

# ── 参数默认值 ────────────────────────────────────────
COUNT=500
EPOCHS=60
MODEL="yolo11m.pt"
IMGSZ=640
BATCH=16
DEVICE=0
NAME="yolo_ui"

# ── 解析命令行 ─────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --count)   COUNT="$2";   shift 2 ;;
        --epochs)  EPOCHS="$2";  shift 2 ;;
        --model)   MODEL="$2";   shift 2 ;;
        --imgsz)   IMGSZ="$2";   shift 2 ;;
        --batch)   BATCH="$2";   shift 2 ;;
        --device)  DEVICE="$2";  shift 2 ;;
        --name)    NAME="$2";    shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "=================================================="
echo "  STEP 1 / 3 — 安装依赖"
echo "=================================================="
pip install ultralytics Pillow playwright -q
playwright install chromium

echo ""
echo "=================================================="
echo "  STEP 2 / 3 — 生成合成数据集 (${COUNT} 张)"
echo "=================================================="
python -m generator.main --count "$COUNT"

# 统计实际生成量
N_TRAIN=$(find dataset/images/train -name "*.jpg" 2>/dev/null | wc -l)
N_VAL=$(find dataset/images/val   -name "*.jpg" 2>/dev/null | wc -l)
echo ""
echo "  数据集: ${N_TRAIN} train / ${N_VAL} val"

echo ""
echo "=================================================="
echo "  STEP 3 / 3 — YOLOv11 训练"
echo "=================================================="
yolo detect train \
    model="$MODEL" \
    data=dataset/data.yaml \
    epochs="$EPOCHS" \
    imgsz="$IMGSZ" \
    batch="$BATCH" \
    device="$DEVICE" \
    name="$NAME" \
    project=runs

echo ""
echo "=================================================="
echo "  导出 ONNX"
echo "=================================================="
yolo export \
    model="runs/${NAME}/weights/best.pt" \
    format=onnx \
    imgsz="$IMGSZ"

echo ""
echo "=================================================="
echo "  全部完成！"
echo "  模型:   runs/${NAME}/weights/best.pt"
echo "  ONNX:   runs/${NAME}/weights/best.onnx"
echo "  曲线:   runs/${NAME}/results.csv"
echo "=================================================="
