"""YOLO11 模型测试脚本 — 本地验证用
支持两种模式：
  val  : yolo val（需要 best.pt，出 mAP 指标）
  vis  : ONNX 可视化（需要 best.onnx，生成标注图）
  all  : 两个都跑（默认）
用法：python test_model.py [val|vis|all]
"""
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT = Path(__file__).parent
PT = PROJECT / "runs" / "detect" / "yolo_ui" / "weights" / "best.pt"
ONNX = PROJECT / "best.onnx"
DATA_YAML = PROJECT / "dataset" / "data.yaml"
IMAGES = PROJECT / "dataset" / "images"
CLASSES = ["button", "input", "checkbox", "radio", "select", "textarea", "link", "icon", "modal"]

# ── 模式选择 ──
mode = sys.argv[1] if len(sys.argv) > 1 else "all"


def run_val():
    """yolo val — 出 mAP、Recall、per-class 指标"""
    import subprocess

    if not PT.exists():
        print(f"[SKIP] best.pt 不存在，跳过 val")
        return

    print("=" * 50)
    print("YOLO VAL — 验证集评估")
    print("=" * 50)
    subprocess.run([
        "yolo", "val",
        f"model={PT}",
        f"data={DATA_YAML}",
        "imgsz=640", "batch=4", "device=0",
    ], check=False)

    # 找最新的 val 输出
    runs = sorted((PROJECT / "runs" / "detect").glob("val*"), key=lambda p: p.stat().st_mtime)
    if runs:
        latest = runs[-1]
        results = latest / "results.csv"
        if results.exists():
            print(f"\n详细结果: {latest}/")


def run_vis():
    """ONNX 可视化 — 跑 N 张图，生成标注结果 + 统计"""
    import cv2
    import numpy as np

    if not ONNX.exists():
        print(f"[SKIP] best.onnx 不存在，跳过 vis")
        return

    out_dir = PROJECT / f"test_output_{datetime.now().strftime('%m%d_%H%M')}"
    out_dir.mkdir(exist_ok=True)

    img_files = sorted(IMAGES.glob("**/*.jpg"))[:50]  # 最多 50 张（train+val 子目录）
    if not img_files:
        print(f"[SKIP] {IMAGES} 里没图")
        return

    print("=" * 50)
    print(f"ONNX VIS — {len(img_files)} 张图可视化")
    print("=" * 50)

    net = cv2.dnn.readNet(str(ONNX))
    stats = {}  # class -> count

    for idx, img_path in enumerate(img_files):
        img = cv2.imread(str(img_path))
        if img is None:
            continue
        h, w = img.shape[:2]

        blob = cv2.dnn.blobFromImage(img, 1/255.0, (640, 640), swapRB=True, crop=False)
        net.setInput(blob)
        preds = net.forward()[0]  # (13, 8400)

        boxes, scores, class_ids = [], [], []
        for i in range(preds.shape[1]):
            cls_scores = preds[4:13, i]
            max_score = float(np.max(cls_scores))
            if max_score < 0.3:
                continue
            max_cls = int(np.argmax(cls_scores))
            cx, cy, bw, bh = preds[0:4, i]
            cx *= w / 640
            cy *= h / 640
            bw *= w / 640
            bh *= h / 640
            x1 = int(cx - bw/2)
            y1 = int(cy - bh/2)
            x2 = int(cx + bw/2)
            y2 = int(cy + bh/2)
            boxes.append([x1, y1, x2 - x1, y2 - y1])
            scores.append(max_score)
            class_ids.append(max_cls)

        # NMS
        if boxes:
            indices = cv2.dnn.NMSBoxes(boxes, scores, 0.5, 0.4)
            if len(indices) > 0:
                for i in indices.flatten():
                    x1, y1, bw, bh = boxes[i]
                    cls_name = CLASSES[class_ids[i]]
                    label = f"{cls_name} {scores[i]:.2f}"
                    stats[cls_name] = stats.get(cls_name, 0) + 1
                    cv2.rectangle(img, (x1, y1), (x1 + bw, y1 + bh), (0, 255, 0), 2)
                    cv2.putText(img, label, (x1, max(y1 - 5, 15)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        out_path = out_dir / img_path.name
        cv2.imwrite(str(out_path), img)

        if (idx + 1) % 10 == 0 or idx == len(img_files) - 1:
            print(f"  [{idx+1}/{len(img_files)}] done")

    # 统计
    print(f"\n检测统计 (conf≥0.3, NMS 0.5):")
    total = sum(stats.values())
    for cls_name in CLASSES:
        count = stats.get(cls_name, 0)
        bar = "█" * (count // 2) if count > 0 else ""
        print(f"  {cls_name:10s} {count:4d}  {bar}")
    print(f"  {'合计':10s} {total:4d}")
    print(f"\n标注图保存在: {out_dir}/")
    print("打开几张看看框得对不对")


# ── 入口 ──
if mode == "val":
    run_val()
elif mode == "vis":
    run_vis()
elif mode == "all":
    run_val()
    print()
    run_vis()
else:
    print(f"用法: python test_model.py [val|vis|all]")
