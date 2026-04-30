#!/bin/bash
# 云机上跑的自动等数据+训练脚本
# 用法: bash auto_train.sh

IMG_DIR="dataset/images"
TARGET=5000
SLEEP_INTERVAL=30  # 每30秒检查一次

echo "[$(date '+%H:%M:%S')] 等数据生成到 ${TARGET} 张..."

while true; do
    # 统计图片数
    count=$(ls "$IMG_DIR"/*.jpg 2>/dev/null | wc -l)
    echo "[$(date '+%H:%M:%S')] 当前: ${count}/${TARGET}"

    if [ "$count" -ge "$TARGET" ]; then
        echo "[$(date '+%H:%M:%S')] 到 ${TARGET} 了，等2分钟后开训..."
        sleep 120

        echo "[$(date '+%H:%M:%S')] 开始训练"
        yolo detect train \
            model=yolo11s.pt \
            data=dataset/data.yaml \
            epochs=60 \
            imgsz=640 \
            batch=16 \
            device=0

        echo "[$(date '+%H:%M:%S')] 训练完成"

        # 导出 ONNX
        echo "[$(date '+%H:%M:%S')] 导出 ONNX..."
        yolo export model=runs/detect/train/weights/best.pt format=onnx imgsz=640

        echo "[$(date '+%H:%M:%S')] 全搞定，保留以下文件："
        echo "  best.pt      -> runs/detect/train/weights/best.pt"
        echo "  best.onnx    -> runs/detect/train/weights/best.onnx"
        echo "  results.csv  -> runs/detect/train/results.csv"
        break
    fi

    sleep $SLEEP_INTERVAL
done
