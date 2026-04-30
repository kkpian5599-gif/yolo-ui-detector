# test_overnight.ps1 — 验证过夜脚本能跑
# 用法: powershell -File test_overnight.ps1

$ErrorActionPreference = "Continue"
$errors = 0
$warns = 0

function Check($label, $test, $isFatal=$false) {
    $ok = $false
    try { $ok = & $test } catch { $ok = $false }
    if ($ok) {
        Write-Host "  [OK] $label" -ForegroundColor Green
    } else {
        if ($isFatal) {
            Write-Host "  [FAIL] $label (致命)" -ForegroundColor Red
            $script:errors++
        } else {
            Write-Host "  [WARN] $label" -ForegroundColor Yellow
            $script:warns++
        }
    }
}

Write-Host "=== 过夜脚本环境检查 ===" -ForegroundColor Cyan
Write-Host ""

# 1. yolo 可用
Check "yolo 命令可用" { yolo --version 2>&1 | Out-Null; $true } $true

# 2. 当前目录是项目根
Check "data.yaml 存在" { Test-Path "dataset/data.yaml" } $true
Check "训练图片存在" { (Get-ChildItem "dataset/images/*.jpg" -ErrorAction SilentlyContinue).Count -gt 0 } $true

# 3. GPU 可用
Check "PyTorch CUDA 可用" {
    $r = python -c "import torch; print(torch.cuda.is_available())" 2>&1
    $r -eq "True"
} $true

# 4. 关键路径
Check "当前 YOLO11s best.pt 存在" {
    Test-Path "runs/detect/train/weights/best.pt"
}

# 5. models 目录可写
Check "models 目录可写" {
    $null = New-Item -ItemType Directory -Force -Path "models" -ErrorAction Stop
    $testFile = "models/.write_test"
    "test" | Out-File $testFile
    Remove-Item $testFile
    $true
} $true

# 6. 磁盘空间 (至少 10GB 给模型和日志)
Check "磁盘空间 ≥ 10GB" {
    $drive = (Get-Location).Drive.Name + ":"
    $free = (Get-PSDrive $drive).Free / 1GB
    $free -ge 10
} $true

# 7. 网络 (下载 yolo11m.pt, ~40MB)
Check "GitHub releases 可达 (yolo11s.pt 已缓存即通过)" {
    # 不实际下载，只检查 DNS
    try {
        $null = [System.Net.Dns]::GetHostEntry("github.com")
        $true
    } catch {
        $false
    }
}

Write-Host ""
Write-Host "=== 结果: $errors 致命错误, $warns 警告 ===" -ForegroundColor Cyan

if ($errors -gt 0) {
    Write-Host "修复以上致命错误后再跑 overnight.ps1" -ForegroundColor Red
    exit 1
} else {
    Write-Host "可以跑了: powershell -File overnight.ps1" -ForegroundColor Green
    exit 0
}
