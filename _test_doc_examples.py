"""
验证 MODEL_USAGE.md 中的代码示例是否正确
使用最近的截图作为测试图片
"""
import sys, os
from pathlib import Path

# 找一张测试图
test_output = Path("test_output")
imgs = sorted(test_output.glob("*.jpg"), key=os.path.getmtime, reverse=True)
if not imgs:
    print("ERROR: test_output/ 里没有截图，请先跑一次 test_screen.py")
    sys.exit(1)

IMAGE_PATH = str(imgs[0])
print(f"使用测试图: {IMAGE_PATH}\n")

# ============================================================
# 测试 1：cv2.dnn 版本（来自文档 Section 4）
# ============================================================
print("=" * 50)
print("测试 1: cv2.dnn 版本")
print("=" * 50)

import cv2
import numpy as np

CLASSES = ["button", "input", "checkbox", "radio", "select",
           "textarea", "link", "icon", "modal"]
INFER_SIZE  = 640
CONF_THRESH = 0.4
NMS_THRESH  = 0.45

net = cv2.dnn.readNet("best.onnx")

def letterbox(img, size=INFER_SIZE):
    h, w = img.shape[:2]
    scale = min(size / w, size / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((size, size, 3), 114, dtype=np.uint8)
    pad_x = (size - nw) // 2
    pad_y = (size - nh) // 2
    canvas[pad_y:pad_y + nh, pad_x:pad_x + nw] = resized
    blob = canvas[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
    blob = blob[np.newaxis]
    return blob, scale, pad_x, pad_y

def detect_cv2(img):
    blob, scale, pad_x, pad_y = letterbox(img)
    net.setInput(blob)
    outputs = net.forward()   # (1, 13, 8400)
    preds = outputs[0]        # (13, 8400)

    boxes, scores, class_ids = [], [], []
    for i in range(preds.shape[1]):
        cls_scores = preds[4:, i]
        max_score = float(np.max(cls_scores))
        if max_score < CONF_THRESH:
            continue
        max_cls = int(np.argmax(cls_scores))
        cx = (preds[0, i] - pad_x) / scale
        cy = (preds[1, i] - pad_y) / scale
        bw = preds[2, i] / scale
        bh = preds[3, i] / scale
        x1 = int(cx - bw / 2)
        y1 = int(cy - bh / 2)
        boxes.append([x1, y1, int(bw), int(bh)])
        scores.append(max_score)
        class_ids.append(max_cls)

    if not boxes:
        return []
    indices = cv2.dnn.NMSBoxes(boxes, scores, CONF_THRESH, NMS_THRESH)
    if len(indices) == 0:
        return []

    results = []
    for idx in indices.flatten():
        x1, y1, bw, bh = boxes[idx]
        results.append({
            "class": CLASSES[class_ids[idx]],
            "conf":  float(scores[idx]),
            "bbox":  (x1, y1, x1 + bw, y1 + bh),
        })
    return results

img = cv2.imread(IMAGE_PATH)
assert img is not None, "图片读取失败"
results1 = detect_cv2(img)
print(f"[OK] cv2.dnn 检测到 {len(results1)} 个元素")
for r in results1:
    print(f"     {r['class']:<10} conf={r['conf']:.0%}  bbox={r['bbox']}")

# ============================================================
# 测试 2：onnxruntime 版本（来自文档 Section 5）
# ============================================================
print()
print("=" * 50)
print("测试 2: onnxruntime 版本")
print("=" * 50)

import onnxruntime as ort

session = ort.InferenceSession(
    "best.onnx",
    providers=["CPUExecutionProvider"]
)

def detect_ort(img):
    blob, scale, pad_x, pad_y = letterbox(img)
    input_name = session.get_inputs()[0].name
    raw = session.run(None, {input_name: blob})[0]  # (1, 13, 8400)
    preds = raw[0]  # (13, 8400)

    boxes, scores, class_ids = [], [], []
    for i in range(preds.shape[1]):
        cls_scores = preds[4:, i]
        max_score = float(np.max(cls_scores))
        if max_score < CONF_THRESH:
            continue
        max_cls = int(np.argmax(cls_scores))
        cx = (preds[0, i] - pad_x) / scale
        cy = (preds[1, i] - pad_y) / scale
        bw = preds[2, i] / scale
        bh = preds[3, i] / scale
        x1 = int(cx - bw / 2)
        y1 = int(cy - bh / 2)
        boxes.append([x1, y1, int(bw), int(bh)])
        scores.append(max_score)
        class_ids.append(max_cls)

    if not boxes:
        return []
    indices = cv2.dnn.NMSBoxes(boxes, scores, CONF_THRESH, NMS_THRESH)
    if len(indices) == 0:
        return []

    results = []
    for idx in indices.flatten():
        x1, y1, bw, bh = boxes[idx]
        results.append({
            "class": CLASSES[class_ids[idx]],
            "conf":  float(scores[idx]),
            "bbox":  (x1, y1, x1 + bw, y1 + bh),
        })
    return results

results2 = detect_ort(img)
print(f"[OK] onnxruntime 检测到 {len(results2)} 个元素")
for r in results2:
    print(f"     {r['class']:<10} conf={r['conf']:.0%}  bbox={r['bbox']}")

# ============================================================
# 对比两个版本结果是否一致
# ============================================================
print()
print("=" * 50)
print("结果对比")
print("=" * 50)
assert len(results1) == len(results2), \
    f"数量不一致! cv2={len(results1)} ort={len(results2)}"
for r1, r2 in zip(sorted(results1, key=lambda x: x['bbox']),
                  sorted(results2, key=lambda x: x['bbox'])):
    assert r1['class'] == r2['class'], f"类别不一致: {r1['class']} vs {r2['class']}"
print("[OK] 两个版本结果完全一致！")
print()
print("所有测试通过 ✅")
