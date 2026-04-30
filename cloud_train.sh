#!/bin/bash
# yolo-ui-detector 云端训练脚本
# 用法: bash cloud_train.sh [small|medium|large|all]
#   small  = yolo11s, 3000图, 80epoch  (基线, ~40min)
#   medium = yolo11m, 5000图, 80epoch  (大模型, ~60min)
#   large  = yolo11s, 5000图, imgsz=1280 (高精度, ~50min)
#   all    = 全部跑一遍 (默认)

set -e

SIZE=${1:-all}
DATA_DIR="dataset"
IMAGES="$DATA_DIR/images"
LABELS="$DATA_DIR/labels"

echo "=== Step 0: Install deps ==="
pip install -e ".[train]" -q
playwright install chromium 2>/dev/null || true

echo "=== Step 1: Generate data ==="
GEN_COUNT=5000
[ "$SIZE" = "small" ] && GEN_COUNT=3000

python -m generator.main $GEN_COUNT

echo "=== Step 2: Train/Val split (90/10) ==="
TOTAL=$(ls $IMAGES/*.jpg 2>/dev/null | wc -l)
VAL=$(( TOTAL / 10 ))
[ $VAL -lt 30 ] && VAL=30

mkdir -p $DATA_DIR/train/images $DATA_DIR/train/labels
mkdir -p $DATA_DIR/val/images $DATA_DIR/val/labels

# 随机选10%当验证集
ls $IMAGES/*.jpg | shuf | head -$VAL | while read f; do
    base=$(basename "$f" .jpg)
    mv "$IMAGES/${base}.jpg" "$DATA_DIR/val/images/" 2>/dev/null || true
    mv "$LABELS/${base}.txt" "$DATA_DIR/val/labels/" 2>/dev/null || true
done
mv $IMAGES/*.jpg $DATA_DIR/train/images/ 2>/dev/null || true
mv $LABELS/*.txt $DATA_DIR/train/labels/ 2>/dev/null || true

# 更新 data.yaml
cat > $DATA_DIR/data.yaml << YEOF
path: $(pwd)/$DATA_DIR
train: train/images
val: val/images

nc: 9
names:
  - button
  - input
  - checkbox
  - radio
  - select
  - textarea
  - link
  - icon
  - modal
YEOF

echo "Train: $(ls $DATA_DIR/train/images/*.jpg 2>/dev/null | wc -l) images"
echo "Val:   $(ls $DATA_DIR/val/images/*.jpg 2>/dev/null | wc -l) images"

# ============================================
do_train() {
    local name=$1 model=$2 epochs=$3 batch=$4 imgsz=${5:-640}
    echo ""
    echo "============================================"
    echo "=== Training: $name ==="
    echo "============================================"
    yolo detect train \
        model=$model \
        data=$DATA_DIR/data.yaml \
        epochs=$epochs \
        imgsz=$imgsz \
        batch=$batch \
        device=0 \
        name=$name \
        exist_ok=True

    echo "=== Export ONNX: $name ==="
    yolo export model=runs/detect/$name/weights/best.pt format=onnx
    echo "=== $name DONE ==="
}

# ============================================
case "$SIZE" in
    small)
        do_train "yolo11s_baseline" "yolo11s.pt" 80 16 640
        ;;
    medium)
        do_train "yolo11m_big" "yolo11m.pt" 80 12 640
        ;;
    large)
        do_train "yolo11s_hires" "yolo11s.pt" 80 8 1280
        ;;
    all)
        echo ""
        echo "  ========================================"
        echo "  FULL DAY PLAN — 3 models"
        echo "  ========================================"
        
        do_train "yolo11s_baseline" "yolo11s.pt" 80 16 640
        do_train "yolo11s_hires" "yolo11s.pt" 80 8 1280
        do_train "yolo11m_big" "yolo11m.pt" 80 12 640
        
        echo ""
        echo "============================================"
        echo "=== ALL TRAINING COMPLETE ==="
        echo "=== Models in runs/detect/ ==="
        echo "============================================"
        ls -la runs/detect/*/weights/best.onnx 2>/dev/null
        ;;
esac

echo ""
echo "=== Done! Download ONNX files to local ==="
echo "scp -r user@this-host:~/yolo-ui-detector/runs/detect/*/weights/best.onnx ./"
echo "THEN SHUTDOWN THE CLOUD MACHINE!"
