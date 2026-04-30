# overnight.ps1 — GPU 过夜训练脚本
# 云机 Win10 直接用，无需 venv
# 用法: powershell -File overnight.ps1

$ErrorActionPreference = "Continue"
$logPath = "overnight_log.txt"
$startTime = Get-Date

# --- 工具函数 ---
function Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $logPath -Value $line
}

function Run-Step($stepName, $command) {
    Log ">>> $stepName"
    Log "    命令: $command"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $out = Invoke-Expression $command 2>&1 | Out-String
    $sw.Stop()
    $ok = ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null)
    $elapsed = [math]::Round($sw.Elapsed.TotalMinutes, 1)
    if ($ok) {
        Log "    完成 (${elapsed}min)"
    } else {
        Log "    失败 (exit=$LASTEXITCODE, ${elapsed}min)"
        Log "    输出: $($out -join ' ' | Select-Object -First 200)"
    }
    return @{ok=$ok; out=$out}
}

# --- 入口 ---
Log "========================================"
Log "  过夜训练开始"
Log "  开始时间: $startTime"
Log "========================================"

# 前置检查
if (-not (Test-Path "dataset/data.yaml")) {
    Log "FATAL: dataset/data.yaml 不存在，当前目录错误"
    exit 1
}

try {
    $yoloVer = yolo --version 2>&1
    Log "yolo: $yoloVer"
} catch {
    Log "FATAL: yolo 命令不可用"
    exit 1
}

$dataCount = (Get-ChildItem "dataset/images/*.jpg").Count
Log "数据集: $dataCount 张图片"

# 创建输出目录
$null = New-Item -ItemType Directory -Force -Path "models"

# ========================================================
# Step 1: 导出当前 YOLO11s（60epoch）→ ONNX
# ========================================================
Log ""
Log "===== Step 1/5: 导出 YOLO11s ======"

if (Test-Path "runs/detect/train/weights/best.pt") {
    $r = Run-Step "导出 ONNX" "yolo export model=runs/detect/train/weights/best.pt format=onnx imgsz=640"
    if ($r.ok) {
        $srcOnnx = "runs/detect/train/weights/best.onnx"
        if (Test-Path $srcOnnx) {
            Copy-Item $srcOnnx "models/yolo11s_60ep.onnx" -Force
            Log "    → models/yolo11s_60ep.onnx"
        } else {
            Log "    ⚠ best.onnx 未生成，检查 export 输出"
        }
    }
} else {
    Log "    SKIP: runs/detect/train/weights/best.pt 不存在"
}

# ========================================================
# Step 2: 训练 YOLO11m
# ========================================================
Log ""
Log "===== Step 2/5: 训练 YOLO11m ====="

$r = Run-Step "训练 YOLO11m 60 epochs" "yolo detect train model=yolo11m.pt data=dataset/data.yaml epochs=60 imgsz=640 batch=48 device=0"

# ========================================================
# Step 3: 导出 YOLO11m → ONNX
# ========================================================
Log ""
Log "===== Step 3/5: 导出 YOLO11m ====="

$m11mBest = "runs/detect/train2/weights/best.pt"
if (Test-Path $m11mBest) {
    $r = Run-Step "导出 ONNX" "yolo export model=$m11mBest format=onnx imgsz=640"
    if ($r.ok) {
        $srcOnnx = "runs/detect/train2/weights/best.onnx"
        if (Test-Path $srcOnnx) {
            Copy-Item $srcOnnx "models/yolo11m_60ep.onnx" -Force
            Log "    → models/yolo11m_60ep.onnx"
        }
    }
} else {
    Log "    SKIP: $m11mBest 不存在（Step 2 可能失败）"
}

# ========================================================
# Step 4: YOLO11s 微调 30 epochs（lr 减半）
# ========================================================
Log ""
Log "===== Step 4/5: YOLO11s 微调 ====="

$m11sBest = "runs/detect/train/weights/best.pt"
if (Test-Path $m11sBest) {
    $r = Run-Step "微调 YOLO11s 30 epochs" "yolo detect train model=$m11sBest data=dataset/data.yaml epochs=30 imgsz=640 batch=64 lr0=0.0005 device=0"
} else {
    Log "    SKIP: $m11sBest 不存在"
}

# ========================================================
# Step 5: 导出微调后的 YOLO11s → ONNX
# ========================================================
Log ""
Log "===== Step 5/5: 导出微调 YOLO11s ====="

$m11sFineBest = "runs/detect/train3/weights/best.pt"
if (Test-Path $m11sFineBest) {
    $r = Run-Step "导出 ONNX" "yolo export model=$m11sFineBest format=onnx imgsz=640"
    if ($r.ok) {
        $srcOnnx = "runs/detect/train3/weights/best.onnx"
        if (Test-Path $srcOnnx) {
            Copy-Item $srcOnnx "models/yolo11s_90ep.onnx" -Force
            Log "    → models/yolo11s_90ep.onnx"
        }
    }
} else {
    Log "    SKIP: $m11sFineBest 不存在（Step 4 可能失败）"
}

# ========================================================
# 汇总
# ========================================================
Log ""
Log "========================================"
Log "  过夜训练完成"
$elapsed = [math]::Round(((Get-Date) - $startTime).TotalHours, 1)
Log "  总耗时: ${elapsed}h"
Log "  产出模型:"
Get-ChildItem models/*.onnx | ForEach-Object { Log "    models/$($_.Name) ($([math]::Round($_.Length/1MB,1))MB)" }
if (-not (Get-ChildItem models/*.onnx)) {
    Log "    ⚠ 无 ONNX 产出，检查上面日志"
}
Log "  日志文件: $logPath"
Log "========================================"
