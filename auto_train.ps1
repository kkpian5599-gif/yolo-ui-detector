# Windows 版自动等数据+训练脚本
# 用法: 在 yolo_data 目录下 powershell -File auto_train.ps1

$imgDir = "dataset\images"
$target = 5000
$sleepInterval = 30   # 每30秒检查
$waitAfter = 120      # 到目标后等2分钟

Write-Host "$(Get-Date -Format 'HH:mm:ss') 等数据生成到 $target 张..."

while ($true) {
    $count = (Get-ChildItem "$imgDir\*.jpg" -ErrorAction SilentlyContinue).Count
    Write-Host "$(Get-Date -Format 'HH:mm:ss') 当前: $count/$target"

    if ($count -ge $target) {
        Write-Host "$(Get-Date -Format 'HH:mm:ss') 到 $target 了，等2分钟后开训..."
        Start-Sleep -Seconds $waitAfter

        Write-Host "$(Get-Date -Format 'HH:mm:ss') 开始训练"
        yolo detect train model=yolo11s.pt data=dataset/data.yaml epochs=60 imgsz=640 batch=16 device=0
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "训练失败! exit code: $LASTEXITCODE"
            break
        }

        Write-Host "$(Get-Date -Format 'HH:mm:ss') 训练完成"

        Write-Host "$(Get-Date -Format 'HH:mm:ss') 导出 ONNX..."
        yolo export model=runs/detect/train/weights/best.pt format=onnx imgsz=640

        Write-Host "$(Get-Date -Format 'HH:mm:ss') 全搞定，保留以下文件："
        Write-Host "  best.pt      -> runs\detect\train\weights\best.pt"
        Write-Host "  best.onnx    -> runs\detect\train\weights\best.onnx"
        Write-Host "  results.csv  -> runs\detect\train\results.csv"
        break
    }

    Start-Sleep -Seconds $sleepInterval
}
