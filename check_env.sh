#!/bin/bash
# 云端环境检查脚本
# 用法: bash check_env.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0
warn=0

check() {
    local name=$1
    shift
    if "$@" &>/dev/null; then
        echo -e "  ${GREEN}[PASS]${NC} $name"
        ((pass++))
    else
        echo -e "  ${RED}[FAIL]${NC} $name"
        ((fail++))
    fi
}

info() {
    echo -e "  ${YELLOW}[INFO]${NC} $1"
}

echo "============================================"
echo " YOLO-UI-Detector 环境检查"
echo "============================================"

# --- System ---
echo ""
echo "--- System ---"
info "OS: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '"' || uname -a)"
info "Kernel: $(uname -r)"
info "CPU: $(nproc) cores"
info "RAM: $(free -h | awk '/^Mem:/{print $2}')"
info "Disk: $(df -h / | awk 'NR==2{print $4 " free / " $2 " total"}')"

# --- GPU ---
echo ""
echo "--- GPU ---"
if command -v nvidia-smi &>/dev/null; then
    info "$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo 'GPU detected but query failed')"
    check "nvidia-smi works" nvidia-smi -L
    check "CUDA drivers" nvidia-smi -q -d COMPUTE
else
    check "nvidia-smi installed" false
fi

# --- Python ---
echo ""
echo "--- Python ---"
check "python3 exists" python3 --version
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "unknown")
info "Python version: $PY_VER"
check "pip works" python3 -m pip --version

# --- PyTorch ---
echo ""
echo "--- PyTorch ---"
python3 -c "
import torch
print(f'  [INFO] torch: {torch.__version__}')
cuda_ok = torch.cuda.is_available()
print(f'  {\"[PASS]\" if cuda_ok else \"[FAIL]\"} CUDA available')
if cuda_ok:
    print(f'  [INFO] Device: {torch.cuda.get_device_name(0)}')
    print(f'  [INFO] VRAM: {torch.cuda.get_device_properties(0).total_mem / 1024**3:.1f} GB')
    print(f'  [INFO] CUDA version: {torch.version.cuda}')
    print(f'  [INFO] cuDNN: {torch.backends.cudnn.version()}')
" 2>/dev/null || echo "  [FAIL] PyTorch not installed"

# --- Core deps ---
echo ""
echo "--- Dependencies ---"
check "ultralytics" python3 -c "import ultralytics; print(f'  [INFO] version: {ultralytics.__version__}')" 2>/dev/null
check "playwright" python3 -c "import playwright" 2>/dev/null
check "opencv" python3 -c "import cv2" 2>/dev/null
check "numpy" python3 -c "import numpy" 2>/dev/null

# --- Playwright browsers ---
echo ""
echo "--- Playwright Browsers ---"
if python3 -c "import playwright" 2>/dev/null; then
    python3 -c "
from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        print('  [PASS] Chromium launch OK')
        b.close()
except Exception as e:
    print(f'  [FAIL] Chromium launch failed: {e}')
" 2>/dev/null
fi

# --- Project files ---
echo ""
echo "--- Project ---"
[ -f "generator/main.py" ] && check "generator/main.py exists" true || check "generator/main.py exists" false
[ -f "generator/config.py" ] && check "generator/config.py exists" true || check "generator/config.py exists" false
[ -f "collected/style_profile.json" ] && check "style_profile.json exists" true || check "style_profile.json exists" false
[ -d "dataset" ] && check "dataset/ dir exists" true || check "dataset/ dir exists" false

# --- Free space estimate for 5000 images ---
FREE_GB=$(df -BG / | awk 'NR==2{gsub(/G/,"",$4); print $4}')
echo ""
echo "--- Storage ---"
info "Free space: ${FREE_GB}GB"
if [ "$FREE_GB" -lt 2 ]; then
    echo -e "  ${RED}[WARN]${NC} Less than 2GB free — 5000 images need ~150MB, training artifacts ~500MB"
elif [ "$FREE_GB" -lt 5 ]; then
    echo -e "  ${YELLOW}[INFO]${NC} 2-5GB free — tight but enough"
else
    echo -e "  ${GREEN}[PASS]${NC} 5+GB free — plenty"
fi

# --- Summary ---
echo ""
echo "============================================"
echo -e " Results: ${GREEN}$pass passed${NC}, ${RED}$fail failed${NC}"
echo "============================================"

if [ $fail -gt 0 ]; then
    echo ""
    echo "Fix failures before running cloud_train.sh:"
    echo "  pip install -e '.[train]'"
    echo "  playwright install chromium"
    exit 1
else
    echo "Ready to train! Run: bash cloud_train.sh all"
    exit 0
fi
