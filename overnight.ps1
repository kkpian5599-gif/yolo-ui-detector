# overnight.ps1 - GPU overnight training pipeline
# Cloud Win10, direct Python (no venv)
# Usage: powershell -File overnight.ps1

$ErrorActionPreference = "Continue"
$logPath = "overnight_log.txt"
$startTime = Get-Date

function Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $logPath -Value $line
}

function Run-Step($stepName, $command) {
    Log ">>> $stepName"
    Log "    cmd: $command"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $out = Invoke-Expression $command 2>&1 | Out-String
    $sw.Stop()
    $ok = ($LASTEXITCODE -eq 0 -or $LASTEXITCODE -eq $null)
    $elapsed = [math]::Round($sw.Elapsed.TotalMinutes, 1)
    if ($ok) {
        Log "    OK (${elapsed}min)"
    } else {
        Log "    FAIL (exit=$LASTEXITCODE, ${elapsed}min)"
        $short = $out.Substring(0, [math]::Min(300, $out.Length))
        Log "    output: $short"
    }
    return @{ok=$ok; out=$out}
}

Log "========================================"
Log "  Overnight training pipeline"
Log "  Start: $startTime"
Log "========================================"

# Pre-flight
if (-not (Test-Path "dataset/data.yaml")) {
    Log "FATAL: dataset/data.yaml not found - wrong directory?"
    exit 1
}
try {
    $yoloVer = yolo --version 2>&1
    Log "yolo: $yoloVer"
} catch {
    Log "FATAL: yolo command not available"
    exit 1
}
$imgCount = (Get-ChildItem "dataset/images/*.jpg").Count
Log "Dataset: $imgCount images"
$null = New-Item -ItemType Directory -Force -Path "models"

# ============================================================
# Step 1: Export current YOLO11s (60ep) to ONNX
# ============================================================
Log ""
Log "===== Step 1/5: Export YOLO11s ====="

if (Test-Path "runs/detect/train/weights/best.pt") {
    $r = Run-Step "Export ONNX" "yolo export model=runs/detect/train/weights/best.pt format=onnx imgsz=640"
    if ($r.ok) {
        $src = "runs/detect/train/weights/best.onnx"
        if (Test-Path $src) {
            Copy-Item $src "models/yolo11s_60ep.onnx" -Force
            $sizeMB = [math]::Round((Get-Item $src).Length / 1048576, 1)
            Log "    -> models/yolo11s_60ep.onnx (${sizeMB}MB)"
        } else {
            Log "    WARN: best.onnx not generated"
        }
    }
} else {
    Log "    SKIP: best.pt not found"
}

# ============================================================
# Step 2: Train YOLO11m
# ============================================================
Log ""
Log "===== Step 2/5: Train YOLO11m ====="

$r = Run-Step "Train YOLO11m 60ep" "yolo detect train model=yolo11m.pt data=dataset/data.yaml epochs=60 imgsz=640 batch=48 device=0"

# ============================================================
# Step 3: Export YOLO11m to ONNX
# ============================================================
Log ""
Log "===== Step 3/5: Export YOLO11m ====="

$m11mBest = "runs/detect/train2/weights/best.pt"
if (Test-Path $m11mBest) {
    $r = Run-Step "Export ONNX" "yolo export model=$m11mBest format=onnx imgsz=640"
    if ($r.ok) {
        $src = "runs/detect/train2/weights/best.onnx"
        if (Test-Path $src) {
            Copy-Item $src "models/yolo11m_60ep.onnx" -Force
            $sizeMB = [math]::Round((Get-Item $src).Length / 1048576, 1)
            Log "    -> models/yolo11m_60ep.onnx (${sizeMB}MB)"
        }
    }
} else {
    Log "    SKIP: $m11mBest not found (Step 2 may have failed)"
}

# ============================================================
# Step 4: Fine-tune YOLO11s 30 more epochs (lr halved)
# ============================================================
Log ""
Log "===== Step 4/5: Fine-tune YOLO11s ====="

$m11sBest = "runs/detect/train/weights/best.pt"
if (Test-Path $m11sBest) {
    $r = Run-Step "Fine-tune 30ep" "yolo detect train model=$m11sBest data=dataset/data.yaml epochs=30 imgsz=640 batch=64 lr0=0.0005 device=0"
} else {
    Log "    SKIP: $m11sBest not found"
}

# ============================================================
# Step 5: Export fine-tuned YOLO11s to ONNX
# ============================================================
Log ""
Log "===== Step 5/5: Export fine-tuned YOLO11s ====="

$m11sFineBest = "runs/detect/train3/weights/best.pt"
if (Test-Path $m11sFineBest) {
    $r = Run-Step "Export ONNX" "yolo export model=$m11sFineBest format=onnx imgsz=640"
    if ($r.ok) {
        $src = "runs/detect/train3/weights/best.onnx"
        if (Test-Path $src) {
            Copy-Item $src "models/yolo11s_90ep.onnx" -Force
            $sizeMB = [math]::Round((Get-Item $src).Length / 1048576, 1)
            Log "    -> models/yolo11s_90ep.onnx (${sizeMB}MB)"
        }
    }
} else {
    Log "    SKIP: $m11sFineBest not found (Step 4 may have failed)"
}

# ============================================================
# Summary
# ============================================================
Log ""
Log "========================================"
Log "  Pipeline finished"
$elapsed = [math]::Round(((Get-Date) - $startTime).TotalHours, 1)
Log "  Total time: ${elapsed}h"
Log "  Output models:"
$modelFiles = Get-ChildItem models/*.onnx -ErrorAction SilentlyContinue
if ($modelFiles) {
    foreach ($f in $modelFiles) {
        $mb = [math]::Round($f.Length / 1048576, 1)
        Log "    models/$($f.Name) (${mb}MB)"
    }
} else {
    Log "    WARN: No ONNX files produced - check log above"
}
Log "  Log file: $logPath"
Log "========================================"
