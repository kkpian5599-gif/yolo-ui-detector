#!/bin/bash
# 青椒云 3090 裸机一键引导脚本
# 从零装环境 + 拉代码 + 开训

set -e

echo "============================================"
echo " YOLO-UI-Detector 裸机引导"
echo "============================================"

# --- Step 0: 换国内源 ---
echo ""
echo "=== Step 0: 换清华源 ==="
sudo sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list 2>/dev/null || true
sudo sed -i 's/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list 2>/dev/null || true

# --- Step 1: 装基础包 ---
echo ""
echo "=== Step 1: 装基础包 ==="
sudo apt update -qq
sudo apt install -y -qq python3 python3-pip python3-venv unzip wget

# --- Step 2: 下载代码 ---
echo ""
echo "=== Step 2: 下载代码 ==="
CODE_URL="https://github.com/kkpian5599-gif/yolo-ui-detector/archive/refs/heads/master.zip"
wget -q --show-progress "$CODE_URL" -O yolo-ui-detector.zip
unzip -q yolo-ui-detector.zip
mv yolo-ui-detector-master yolo-ui-detector
cd yolo-ui-detector
echo "Code ready at: $(pwd)"

# --- Step 3: 创建 venv ---
echo ""
echo "=== Step 3: 创建 Python 虚拟环境 ==="
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip -q

# --- Step 4: 装 PyTorch CUDA 版 ---
echo ""
echo "=== Step 4: 装 PyTorch (CUDA 12.1) ==="
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121 -q

# --- Step 5: 装项目依赖 ---
echo ""
echo "=== Step 5: 装项目依赖 ==="
pip install -e ".[train]" -q

# --- Step 6: 装 Playwright + Chromium ---
echo ""
echo "=== Step 6: 装 Playwright + Chromium ==="
playwright install --with-deps chromium

# --- Step 7: 下载 yolo 预训练权重 ---
echo ""
echo "=== Step 7: 下载预训练权重 ==="
wget -q https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11s.pt -O yolo11s.pt &
wget -q https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo11m.pt -O yolo11m.pt &
wait
echo "Weights downloaded"

# --- Step 8: 环境检查 ---
echo ""
echo "=== Step 8: 环境检查 ==="
bash check_env.sh

echo ""
echo "============================================"
echo " 环境就绪！开始训练："
echo "   bash cloud_train.sh all"
echo "============================================"
