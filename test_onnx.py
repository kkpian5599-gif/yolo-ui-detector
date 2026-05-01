"""快速测试 ONNX 模型预测效果"""
import cv2
import numpy as np
from pathlib import Path

MODEL = Path(__file__).parent / "best.onnx"
IMAGES = list((Path(__file__).parent / "dataset" / "images").glob("*.jpg"))[:5]
CLASSES = ["button", "input", "checkbox", "radio", "select", "textarea", "link", "icon", "modal"]
OUTPUT = Path(__file__).parent / "test_output"
OUTPUT.mkdir(exist_ok=True)

net = cv2.dnn.readNet(str(MODEL))
print(f"Loaded ONNX model: {MODEL}")
print(f"Testing {len(IMAGES)} images...")

for img_path in IMAGES:
    img = cv2.imread(str(img_path))
    h, w = img.shape[:2]

    # YOLO11 expects RGB, 640x640
    blob = cv2.dnn.blobFromImage(img, 1/255.0, (640, 640), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward()  # (1, 13, 8400) = 4 bbox + 9 class scores

    preds = outputs[0]  # (13, 8400)
    boxes, scores, class_ids = [], [], []

    for i in range(preds.shape[1]):
        # class scores start at index 4
        cls_scores = preds[4:13, i]
        max_score = float(np.max(cls_scores))
        if max_score < 0.5:
            continue
        max_cls = int(np.argmax(cls_scores))

        # bbox: cx, cy, w, h (normalized 0-1)
        cx, cy, bw, bh = preds[0:4, i]
        # denormalize to image size
        cx = cx * w / 640
        cy = cy * h / 640
        bw = bw * w / 640
        bh = bh * h / 640

        x1 = int(cx - bw / 2)
        y1 = int(cy - bh / 2)
        x2 = int(cx + bw / 2)
        y2 = int(cy + bh / 2)

        boxes.append([x1, y1, x2 - x1, y2 - y1])
        scores.append(max_score)
        class_ids.append(max_cls)

    # NMS
    if boxes:
        indices = cv2.dnn.NMSBoxes(boxes, scores, 0.5, 0.4)
        if len(indices) > 0:
            for idx in indices.flatten():
                x1, y1, bw, bh = boxes[idx]
                label = f"{CLASSES[class_ids[idx]]} {scores[idx]:.2f}"
                cv2.rectangle(img, (x1, y1), (x1 + bw, y1 + bh), (0, 255, 0), 2)
                cv2.putText(img, label, (x1, max(y1 - 5, 15)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    out_path = OUTPUT / img_path.name
    cv2.imwrite(str(out_path), img)
    print(f"  {img_path.name}: {len(indices) if boxes else 0} detections -> {out_path}")

print(f"\nDone. Results in {OUTPUT}/")
