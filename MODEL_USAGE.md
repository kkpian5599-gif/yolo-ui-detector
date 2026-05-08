# YOLO UI 元素检测模型 — 完整使用手册

> 模型版本：YOLO11m &nbsp;|&nbsp; 导出格式：ONNX &nbsp;|&nbsp; 输入尺寸：640×640 &nbsp;|&nbsp; 类别数：9

---

## 目录

1. [模型概述](#1-模型概述)
2. [输入输出格式](#2-输入输出格式)
3. [核心注意事项](#3-核心注意事项)
4. [Python 示例（cv2.dnn）](#4-python-示例cv2dnn)
5. [Python 示例（onnxruntime）](#5-python-示例onnxruntime)
6. [Node.js 示例](#6-nodejs-示例)
7. [高分辨率截图处理](#7-高分辨率截图处理)
8. [常见问题](#8-常见问题)

---

## 1. 模型概述

| 属性 | 值 |
|------|-----|
| 架构 | YOLO11m |
| 文件 | `best.onnx`（约 76–80 MB） |
| 输入尺寸 | **固定 640×640**（OpenCV DNN 不支持动态尺寸） |
| 推理设备 | CPU / CUDA |
| 训练数据 | 合成 UI 截图，5000 张，150 epoch |
| mAP50-95 | 0.901（合成验证集） |

### 可检测的 9 种 UI 元素

| ID | 类别 | 说明 |
|----|------|------|
| 0 | `button` | 各种点击按钮 |
| 1 | `input` | 单行文本输入框 |
| 2 | `checkbox` | 复选框 |
| 3 | `radio` | 单选框 |
| 4 | `select` | 下拉选择框 |
| 5 | `textarea` | 多行文本框 |
| 6 | `link` | 超链接 |
| 7 | `icon` | 图标 |
| 8 | `modal` | 弹窗 / 遮罩层 |

---

## 2. 输入输出格式

### 输入 Tensor

```
shape : (1, 3, 640, 640)
dtype : float32
值域  : [0.0, 1.0]
通道  : RGB（注意：OpenCV 默认 BGR，使用前需转换）
预处理: Letterbox（等比缩放 + 灰色填充，填充值 114）
```

### 输出 Tensor

```
shape : (1, 13, 8400)
         │   │    └── anchor 数量（640/8²+ 640/16² + 640/32² = 6400+1600+400）
         │   └────── 4 个坐标 + 9 个类别分数
         └────────── batch size
```

#### 逐行含义

| 行索引 | 含义 | 坐标空间 |
|--------|------|---------|
| 0 | cx（中心 x） | **模型输入空间**（0–640） |
| 1 | cy（中心 y） | **模型输入空间**（0–640） |
| 2 | bw（宽度） | **模型输入空间** |
| 3 | bh（高度） | **模型输入空间** |
| 4–12 | 各类别置信度分数 | — |

> ⚠️ **坐标还原**：模型输出的坐标在 640×640 空间内，必须经过 **逆 Letterbox 变换** 才能还原到原图坐标，见下文代码。

---

## 3. 核心注意事项

### ① 固定输入尺寸 640×640

模型用 `imgsz=640` 导出，内部 Attention 层的 Reshape 操作依赖固定 shape。  
**不能**传入其他尺寸的 blob（如 1280×1280）——会报 `computeShapeByReshapeMask` 错误。

### ② 必须做 Letterbox，不能直接 resize

直接 `cv2.resize(img, (640,640))` 会改变宽高比，导致检测框坐标严重偏移。  
正确做法：等比缩放后在两侧/上下填充灰色（RGB 114,114,114）。

### ③ 颜色通道：BGR → RGB

OpenCV 读取图片是 BGR，但模型训练时用 RGB。  
必须在送入模型前转换：`img[:, :, ::-1]` 或 `cv2.cvtColor(img, cv2.COLOR_BGR2RGB)`。

### ④ 高分辨率截图需要裁剪

| 截图尺寸 | 按钮在 640px 内的宽度 | 效果 |
|---------|-----------------|------|
| 2560×1440（4K） | ~25px | ❌ 识别率低 |
| 1920×1080（FHD） | ~33px | ⚠️ 一般 |
| 1366×768 | ~47px | ✅ 接近训练分布 |

**解决方案**：截图前只截浏览器内容区域（去掉书签栏、任务栏），或将浏览器窗口调整到 ~1280×800。

### ⑤ NMS 参数建议

```
置信度阈值  CONF_THRESH = 0.4   # 降低到 0.2 可检测更多，但误报增加
IoU 阈值    NMS_THRESH  = 0.45
```

---

## 4. Python 示例（cv2.dnn）

### 依赖

```bash
pip install opencv-python numpy
```

### 完整代码

```python
import cv2
import numpy as np

# ── 配置 ──────────────────────────────────────────────
CLASSES = ["button", "input", "checkbox", "radio", "select",
           "textarea", "link", "icon", "modal"]
INFER_SIZE  = 640
CONF_THRESH = 0.4
NMS_THRESH  = 0.45

# ── 加载模型 ─────────────────────────────────────────
net = cv2.dnn.readNet("best.onnx")
# 可选：使用 CUDA 加速
# net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
# net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)


def letterbox(img: np.ndarray, size: int = INFER_SIZE):
    """等比缩放 + 灰边填充，返回 (blob, scale, pad_x, pad_y)"""
    h, w = img.shape[:2]
    scale = min(size / w, size / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((size, size, 3), 114, dtype=np.uint8)
    pad_x = (size - nw) // 2
    pad_y = (size - nh) // 2
    canvas[pad_y:pad_y + nh, pad_x:pad_x + nw] = resized
    # BGR→RGB, HWC→NCHW, 归一化到 [0,1]
    blob = canvas[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
    blob = blob[np.newaxis]  # shape: (1, 3, 640, 640)
    return blob, scale, pad_x, pad_y


def detect(img: np.ndarray) -> list[dict]:
    """
    输入: BGR numpy 数组 (H, W, 3)
    输出: [{"class": str, "conf": float, "bbox": (x1,y1,x2,y2)}, ...]
          bbox 坐标为原图像素坐标
    """
    blob, scale, pad_x, pad_y = letterbox(img)

    net.setInput(blob)
    outputs = net.forward()  # shape: (1, 13, 8400)
    preds = outputs[0]       # shape: (13, 8400)

    boxes, scores, class_ids = [], [], []

    for i in range(preds.shape[1]):  # 遍历 8400 个 anchor
        cls_scores = preds[4:, i]    # 9 个类别分数
        max_score = float(np.max(cls_scores))
        if max_score < CONF_THRESH:
            continue
        max_cls = int(np.argmax(cls_scores))

        # 逆 Letterbox：从模型坐标还原到原图坐标
        cx = (preds[0, i] - pad_x) / scale
        cy = (preds[1, i] - pad_y) / scale
        bw = preds[2, i] / scale
        bh = preds[3, i] / scale

        x1 = int(cx - bw / 2)
        y1 = int(cy - bh / 2)

        boxes.append([x1, y1, int(bw), int(bh)])  # NMSBoxes 需要 [x,y,w,h]
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
            "bbox":  (x1, y1, x1 + bw, y1 + bh),  # (x1, y1, x2, y2)
        })
    return results


# ── 使用示例 ─────────────────────────────────────────
if __name__ == "__main__":
    img = cv2.imread("screenshot.jpg")
    if img is None:
        raise FileNotFoundError("找不到 screenshot.jpg")

    results = detect(img)
    print(f"检测到 {len(results)} 个 UI 元素：")
    for r in results:
        x1, y1, x2, y2 = r["bbox"]
        print(f"  {r['class']:<10} conf={r['conf']:.0%}  "
              f"bbox=({x1},{y1},{x2},{y2})")

    # 可视化
    for r in results:
        x1, y1, x2, y2 = r["bbox"]
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(img, f"{r['class']} {r['conf']:.0%}",
                    (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
    cv2.imwrite("result.jpg", img)
    print("结果已保存到 result.jpg")
```

---

## 5. Python 示例（onnxruntime）

`onnxruntime` 支持动态推理会话，GPU 加速更方便，推荐生产环境使用。

### 依赖

```bash
pip install onnxruntime opencv-python numpy
# GPU 版（需要 CUDA）：
pip install onnxruntime-gpu opencv-python numpy
```

### 完整代码

```python
import cv2
import numpy as np
import onnxruntime as ort

CLASSES = ["button", "input", "checkbox", "radio", "select",
           "textarea", "link", "icon", "modal"]
INFER_SIZE  = 640
CONF_THRESH = 0.4
NMS_THRESH  = 0.45


def letterbox(img: np.ndarray, size: int = INFER_SIZE):
    """等比缩放 + 灰边填充，返回 (blob_NCHW, scale, pad_x, pad_y)"""
    h, w = img.shape[:2]
    scale = min(size / w, size / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
    canvas = np.full((size, size, 3), 114, dtype=np.uint8)
    pad_x = (size - nw) // 2
    pad_y = (size - nh) // 2
    canvas[pad_y:pad_y + nh, pad_x:pad_x + nw] = resized
    blob = canvas[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
    blob = blob[np.newaxis]  # (1, 3, 640, 640)
    return blob, scale, pad_x, pad_y


def detect(session: ort.InferenceSession, img: np.ndarray,
           conf_thresh: float = CONF_THRESH,
           nms_thresh: float = NMS_THRESH) -> list[dict]:
    """
    输入: BGR numpy 数组 (H, W, 3)
    输出: [{"class": str, "conf": float, "bbox": (x1,y1,x2,y2)}, ...]
    """
    blob, scale, pad_x, pad_y = letterbox(img)

    input_name = session.get_inputs()[0].name
    raw = session.run(None, {input_name: blob})[0]  # shape: (1, 13, 8400)
    preds = raw[0]  # (13, 8400)

    boxes, scores, class_ids = [], [], []

    for i in range(preds.shape[1]):
        cls_scores = preds[4:, i]
        max_score = float(np.max(cls_scores))
        if max_score < conf_thresh:
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

    indices = cv2.dnn.NMSBoxes(boxes, scores, conf_thresh, nms_thresh)
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


# ── 初始化（选择执行后端） ─────────────────────────────
session = ort.InferenceSession(
    "best.onnx",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    # 有 CUDA 自动用 GPU，否则回退 CPU
)

# ── 推理 ─────────────────────────────────────────────
img = cv2.imread("screenshot.jpg")
results = detect(session, img)
for r in results:
    print(f"{r['class']:<10} conf={r['conf']:.0%}  bbox={r['bbox']}")
```

---

## 6. Node.js 示例

### 依赖

```bash
npm install onnxruntime-node sharp
```

### 完整代码（`detect.js`）

```javascript
'use strict';

const ort   = require('onnxruntime-node');
const sharp = require('sharp');

// ── 配置 ────────────────────────────────────────────
const CLASSES     = ['button','input','checkbox','radio','select',
                     'textarea','link','icon','modal'];
const INFER_SIZE  = 640;
const CONF_THRESH = 0.4;
const IOU_THRESH  = 0.45;

// ── Letterbox 预处理 ─────────────────────────────────
/**
 * 等比缩放 + 灰边填充到 INFER_SIZE×INFER_SIZE
 * @param {string} imagePath  图片路径（支持 jpg/png）
 * @returns {{ data: Float32Array, scale: number, padX: number, padY: number }}
 */
async function letterbox(imagePath) {
  const meta = await sharp(imagePath).metadata();
  const srcW = meta.width;
  const srcH = meta.height;

  const scale = Math.min(INFER_SIZE / srcW, INFER_SIZE / srcH);
  const nw    = Math.floor(srcW * scale);
  const nh    = Math.floor(srcH * scale);
  const padX  = Math.floor((INFER_SIZE - nw) / 2);
  const padY  = Math.floor((INFER_SIZE - nh) / 2);

  // 缩放后用灰色 (114,114,114) 填充，输出 RGB raw buffer
  const rawBuf = await sharp(imagePath)
    .resize(nw, nh, { kernel: 'linear' })  // 使用双线性插值，与 OpenCV INTER_LINEAR 一致
    .extend({
      top:    padY,
      bottom: INFER_SIZE - nh - padY,
      left:   padX,
      right:  INFER_SIZE - nw - padX,
      background: { r: 114, g: 114, b: 114 },
    })
    .removeAlpha()
    .raw()
    .toBuffer();   // HWC RGB uint8, length = INFER_SIZE*INFER_SIZE*3

  // 转为 CHW Float32（ONNX 期望格式）
  const pixels = INFER_SIZE * INFER_SIZE;
  const data   = new Float32Array(3 * pixels);
  for (let i = 0; i < pixels; i++) {
    data[i]             = rawBuf[i * 3]     / 255.0;  // R
    data[pixels + i]    = rawBuf[i * 3 + 1] / 255.0;  // G
    data[2 * pixels + i] = rawBuf[i * 3 + 2] / 255.0;  // B
  }

  return { data, scale, padX, padY };
}

// ── IoU 计算（用于 NMS） ─────────────────────────────
function iou(a, b) {
  // a, b: [x1, y1, x2, y2]
  const x1 = Math.max(a[0], b[0]);
  const y1 = Math.max(a[1], b[1]);
  const x2 = Math.min(a[2], b[2]);
  const y2 = Math.min(a[3], b[3]);
  const inter = Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
  const areaA = (a[2] - a[0]) * (a[3] - a[1]);
  const areaB = (b[2] - b[0]) * (b[3] - b[1]);
  return inter / (areaA + areaB - inter + 1e-6);
}

// ── 非极大值抑制 ─────────────────────────────────────
function nms(dets, iouThresh) {
  // 按置信度降序排列
  dets.sort((a, b) => b.conf - a.conf);
  const suppressed = new Set();
  const keep = [];
  for (let i = 0; i < dets.length; i++) {
    if (suppressed.has(i)) continue;
    keep.push(dets[i]);
    for (let j = i + 1; j < dets.length; j++) {
      if (suppressed.has(j)) continue;
      if (iou(dets[i].bbox, dets[j].bbox) > iouThresh) {
        suppressed.add(j);
      }
    }
  }
  return keep;
}

// ── 推理主函数 ───────────────────────────────────────
/**
 * @param {ort.InferenceSession} session  已加载的 ONNX 会话
 * @param {string} imagePath              图片路径
 * @returns {Promise<Array<{class:string, conf:number, bbox:[number,number,number,number]}>>}
 *          bbox 格式: [x1, y1, x2, y2]（原图像素坐标）
 */
async function detect(session, imagePath) {
  const { data, scale, padX, padY } = await letterbox(imagePath);

  // 构造输入 Tensor
  const inputName = session.inputNames[0];
  const tensor = new ort.Tensor('float32', data, [1, 3, INFER_SIZE, INFER_SIZE]);
  const outputMap = await session.run({ [inputName]: tensor });

  // 解析输出
  const outputName = session.outputNames[0];
  const outTensor  = outputMap[outputName];
  const raw        = outTensor.data;           // Float32Array
  const [, , numAnchors] = outTensor.dims;     // 通常 8400

  const dets = [];

  for (let i = 0; i < numAnchors; i++) {
    // preds[row][anchor] = raw[row * numAnchors + i]
    const cxModel = raw[0 * numAnchors + i];
    const cyModel = raw[1 * numAnchors + i];
    const bwModel = raw[2 * numAnchors + i];
    const bhModel = raw[3 * numAnchors + i];

    // 找置信度最高的类别
    let maxScore = -Infinity;
    let maxCls   = 0;
    for (let c = 0; c < CLASSES.length; c++) {
      const s = raw[(4 + c) * numAnchors + i];
      if (s > maxScore) { maxScore = s; maxCls = c; }
    }

    if (maxScore < CONF_THRESH) continue;

    // 逆 Letterbox
    const cx = (cxModel - padX) / scale;
    const cy = (cyModel - padY) / scale;
    const bw = bwModel / scale;
    const bh = bhModel / scale;
    const x1 = Math.round(cx - bw / 2);
    const y1 = Math.round(cy - bh / 2);
    const x2 = Math.round(cx + bw / 2);
    const y2 = Math.round(cy + bh / 2);

    dets.push({
      class: CLASSES[maxCls],
      conf:  maxScore,
      bbox:  [x1, y1, x2, y2],
    });
  }

  return nms(dets, IOU_THRESH);
}

// ── 入口 ─────────────────────────────────────────────
async function main() {
  const modelPath = process.argv[2] || 'best.onnx';
  const imagePath = process.argv[3] || 'screenshot.jpg';

  const session = await ort.InferenceSession.create(modelPath, {
    executionProviders: ['cpu'],   // 换成 'cuda' 使用 GPU
  });
  console.log(`模型加载完成: ${modelPath}`);

  const results = await detect(session, imagePath);
  console.log(`\n检测到 ${results.length} 个 UI 元素：`);
  for (const r of results) {
    const [x1, y1, x2, y2] = r.bbox;
    console.log(
      `  ${r.class.padEnd(10)} conf=${(r.conf * 100).toFixed(1).padStart(5)}%` +
      `  bbox=[${x1},${y1},${x2},${y2}]`
    );
  }
}

main().catch(err => { console.error(err); process.exit(1); });
```

### 运行

```bash
node detect.js best.onnx screenshot.jpg
```

> **注意**：Node.js（Sharp）与 Python（OpenCV）的图像缩放插值算法存在浮点精度差异，
> 边界置信度附近的框可能出现 ±1~2 个差异，属正常现象，核心元素（button、input 等）结果一致。

---

## 7. 高分辨率截图处理

### 问题根源

模型训练时页面尺寸为 1366×768 ~ 1920×1080，按钮在 640px 输入内约 **40–50px** 宽。  
4K 截图（2560×1440）经 Letterbox 缩放后，按钮只剩约 **25px**，导致漏检。

### 解决方案：截图前裁剪

```python
import mss
import numpy as np
import cv2

with mss.mss() as sct:
    # 只截浏览器内容区域，去掉书签栏(~130px)和任务栏(~50px)
    region = {"top": 130, "left": 0, "width": 2560, "height": 1260}
    shot = sct.grab(region)
    img = cv2.cvtColor(np.array(shot), cv2.COLOR_BGRA2BGR)

results = detect(img)  # 此时按钮约 31px，识别率显著提升
```

### 推荐浏览器窗口尺寸

将浏览器调整为 **1280×800** 左右窗口后再截图，效果最接近训练分布。

---

## 8. 常见问题

### Q1：输入超过 640×640 会崩溃

```
cv2.error: computeShapeByReshapeMask assertion failed
```

**原因**：模型用 `imgsz=640` 导出，Attention 层 Reshape 依赖固定 shape。  
**解决**：始终保持 `INFER_SIZE = 640`，通过裁剪原图解决大图问题。

---

### Q2：检测框坐标偏移

**原因**：没有做 Letterbox，或坐标还原时没有减去 `pad_x/pad_y`。  
**检查**：确认代码中使用了 `(cx_model - pad_x) / scale` 公式。

---

### Q3：没有检测到按钮

按顺序排查：
1. 截图分辨率是否过高？→ 裁剪到浏览器内容区
2. 置信度阈值是否过高？→ 尝试 `--conf 0.2`
3. 按钮样式是否特殊（渐变、自定义色）？→ 需要真实数据微调

---

### Q4：推理速度慢

| 环境 | 典型耗时 |
|------|---------|
| CPU（Intel i7） | ~1000ms |
| CPU（4核云服务器） | ~2000ms |
| CUDA GPU（RTX 3090） | ~15ms |

CPU 推理较慢属正常，生产环境建议使用 GPU 或对截图进行区域裁剪减少面积。

---

### Q5：Node.js 版本要求

| 包 | 版本要求 |
|----|---------|
| `onnxruntime-node` | ≥ 1.17 |
| `sharp` | ≥ 0.32 |
| Node.js | ≥ 18 |

---

*文档生成时间：2026-05-02 &nbsp;|&nbsp; 模型训练平台：RTX 3090 云端*
