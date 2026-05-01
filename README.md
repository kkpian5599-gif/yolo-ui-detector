# YOLO11 UI 检测 — 运维手册

## 训练产物：哪些要留、哪些扔

| 文件 | 大小 | 用途 | 留否 |
|------|------|------|------|
| `best.pt` | ~18MB (yolo11s) | 后续微调、`yolo val` 验证 | 必须留 |
| `best.onnx` | ~38MB | 本地推理部署 | 必须留 |
| `results.csv` | 几KB | 训练曲线数据 | 建议留 |
| `last.pt` | 同 best.pt | 断点续训 | 不用 |
| `dataset/` | 几百MB | 训练图+标注 | 生成器能重造 |

## 云机关机前操作清单

```powershell
# 1. 导出 ONNX
yolo export model=runs/detect/train/weights/best.pt format=onnx imgsz=640

# 2. 传回本机（二选一）
# A: 推 GitHub
# B: python -m http.server 8888 → 本机浏览器下载

# 3. 关机
```

## 本地测试

```powershell
python test_model.py          # 全测
python test_model.py val      # 只看 mAP（需要 best.pt）
python test_model.py vis      # 只看标注图（需要 best.onnx）
```

## 硬件分工

| 阶段 | 用什么 | 原因 |
|------|--------|------|
| 训练 | 云机 RTX 3090 | 吃显存 |
| 推理 | 本机 GTX 1060 | ONNX 推理只需训练 1/4 显存 |
| 微调 | 云机（半小时 5毛）或本机 yolo11n | 看钱包 |

## 后期迭代

发现漏检 → 截图给我 → 改生成器补数据 → 云机微调 30 epoch → 更新 ONNX

本机备选：GTX 1060 训 yolo11n，batch=4，5000 张约 2 小时，精度略低但够用。

## 模型规格

| 模型 | 参数 | 文件 | 训 5000 张耗时 |
|------|------|------|---------------|
| yolo11n | 2.6M | ~5MB | 本机 2h / 云机 15min |
| yolo11s | 9.4M | ~18MB | 云机 35min |
| yolo11m | 20M | ~40MB | 云机 50min |

## 常用命令

```powershell
# 训练
yolo detect train model=yolo11s.pt data=dataset/data.yaml epochs=30 imgsz=640 batch=32 device=0

# 验证
yolo val model=best.pt data=dataset/data.yaml imgsz=640 batch=4 device=0

# 导出 ONNX
yolo export model=best.pt format=onnx imgsz=640

# 预测单张
yolo predict model=best.pt source=xxx.jpg imgsz=640 save
```

## 检测类别

```
0: button    1: input     2: checkbox
3: radio     4: select    5: textarea
6: link      7: icon      8: modal
```
