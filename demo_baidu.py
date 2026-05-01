"""demo_baidu.py — 用已训练的 ONNX 模型推理百度首页截图
用法:
  python demo_baidu.py                    # 用 best.onnx，推理百度首页
  python demo_baidu.py --url https://...  # 换目标页
  python demo_baidu.py --model best_500.onnx
  python demo_baidu.py --conf 0.3         # 降低置信度门槛看更多框
  python demo_baidu.py --no-open          # 不自动打开结果图
"""
import argparse
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Windows GBK 终端兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import cv2
import numpy as np
from playwright.sync_api import sync_playwright

# ─── 类别定义 & 颜色 ────────────────────────────────────
CLASSES = ["button", "input", "checkbox", "radio", "select",
           "textarea", "link", "icon", "modal"]

# 每类分配固定颜色 (BGR)
COLORS = {
    "button":   (  0, 200,   0),   # 绿
    "input":    (255, 140,   0),   # 橙
    "checkbox": (255,   0, 200),   # 粉紫
    "radio":    (200,   0, 255),   # 紫
    "select":   (  0, 180, 255),   # 天蓝
    "textarea": (  0, 100, 255),   # 蓝
    "link":     ( 50, 220, 220),   # 青
    "icon":     (180, 180,   0),   # 黄绿
    "modal":    (  0,   0, 255),   # 红
}


def screenshot_url(url: str, width: int = 1366, height: int = 768) -> np.ndarray:
    """用 Playwright 打开网页截图，返回 BGR numpy 数组"""
    print(f"  → 打开: {url}  ({width}×{height})")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(url, wait_until="networkidle", timeout=20_000)
        page.wait_for_timeout(1500)          # 等动画/字体加载
        png_bytes = page.screenshot(full_page=False, type="png")
        browser.close()

    arr = np.frombuffer(png_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    print(f"  → 截图尺寸: {img.shape[1]}×{img.shape[0]}")
    return img


def run_onnx(img: np.ndarray, model_path: str,
             conf_thresh: float = 0.35, nms_thresh: float = 0.45):
    """YOLO ONNX 推理，返回检测结果列表"""
    net = cv2.dnn.readNet(model_path)
    h, w = img.shape[:2]

    blob = cv2.dnn.blobFromImage(
        img, 1 / 255.0, (640, 640), swapRB=True, crop=False
    )
    net.setInput(blob)
    preds = net.forward()[0]          # shape: (13, 8400) or (1, 13, 8400)

    # 兼容不同输出形状
    if preds.ndim == 3:
        preds = preds[0]

    boxes, scores_list, class_ids = [], [], []
    n_classes = len(CLASSES)

    for i in range(preds.shape[1]):
        cls_scores = preds[4: 4 + n_classes, i]
        max_score = float(np.max(cls_scores))
        if max_score < conf_thresh:
            continue
        max_cls = int(np.argmax(cls_scores))

        cx, cy, bw, bh = preds[0:4, i]
        cx = cx * w / 640;  cy = cy * h / 640
        bw = bw * w / 640;  bh = bh * h / 640
        x1 = int(cx - bw / 2);  y1 = int(cy - bh / 2)
        boxes.append([x1, y1, int(bw), int(bh)])
        scores_list.append(max_score)
        class_ids.append(max_cls)

    results = []
    if boxes:
        indices = cv2.dnn.NMSBoxes(boxes, scores_list, conf_thresh, nms_thresh)
        if len(indices) > 0:
            for idx in indices.flatten():
                x, y, bw, bh = boxes[idx]
                results.append({
                    "cls":   CLASSES[class_ids[idx]],
                    "conf":  scores_list[idx],
                    "x1": x, "y1": y,
                    "x2": x + bw, "y2": y + bh,
                })
    return results


def draw_results(img: np.ndarray, results: list) -> np.ndarray:
    """在图像上画检测框 + 标签"""
    out = img.copy()
    for r in results:
        cls   = r["cls"]
        color = COLORS.get(cls, (200, 200, 200))
        x1, y1, x2, y2 = r["x1"], r["y1"], r["x2"], r["y2"]

        # 框
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)

        # 标签背景
        label = f"{cls}  {r['conf']:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        ly = max(y1 - 4, th + 4)
        cv2.rectangle(out, (x1, ly - th - 4), (x1 + tw + 4, ly), color, -1)
        cv2.putText(out, label, (x1 + 2, ly - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    return out


def print_summary(results: list):
    """命令行打印检测统计"""
    from collections import Counter
    counts = Counter(r["cls"] for r in results)
    total  = len(results)

    print(f"\n  ┌── 检测结果汇总 ({'共 ' + str(total) + ' 个元素'}) ──────────────")
    for cls in CLASSES:
        n = counts.get(cls, 0)
        if n == 0:
            continue
        bar = "█" * n
        print(f"  │  {cls:10s}  {n:3d}  {bar}")
    print(f"  └{'─'*40}")

    if results:
        print(f"\n  详细列表 (按置信度排序):")
        for i, r in enumerate(sorted(results, key=lambda x: -x["conf"]), 1):
            print(f"  {i:3d}. [{r['cls']:10s}] conf={r['conf']:.3f}  "
                  f"bbox=({r['x1']},{r['y1']})-({r['x2']},{r['y2']})")


def open_image(path: str):
    """跨平台打开图片"""
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])


# ─── 主流程 ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="ONNX 模型推理演示")
    parser.add_argument("--url",     default="https://www.baidu.com", help="目标网址")
    parser.add_argument("--model",   default="",                       help="ONNX 模型路径（默认自动选）")
    parser.add_argument("--conf",    type=float, default=0.35,         help="置信度门槛 (default: 0.35)")
    parser.add_argument("--width",   type=int,   default=1366,         help="截图宽度")
    parser.add_argument("--height",  type=int,   default=768,          help="截图高度")
    parser.add_argument("--no-open", action="store_true",              help="不自动打开结果图")
    parser.add_argument("--out",     default="",                       help="输出图片路径（默认自动命名）")
    args = parser.parse_args()

    root = Path(__file__).parent

    # ── 选模型 ──
    if args.model:
        model_path = Path(args.model)
    else:
        # 优先用 runs/ 里最新训练出来的，找不到就用根目录的 best.onnx
        candidates = sorted(
            root.glob("runs/detect/*/weights/best.onnx"),
            key=lambda p: p.stat().st_mtime, reverse=True
        )
        if candidates:
            model_path = candidates[0]
            print(f"  ✔ 自动选取最新模型: {model_path}")
        elif (root / "best.onnx").exists():
            model_path = root / "best.onnx"
            print(f"  ✔ 使用根目录模型: {model_path}")
        else:
            print("❌ 找不到 ONNX 模型！请先运行训练，或用 --model 指定路径")
            sys.exit(1)

    if not model_path.exists():
        print(f"❌ 模型文件不存在: {model_path}")
        sys.exit(1)

    # ── 输出路径 ──
    if args.out:
        out_path = Path(args.out)
    else:
        ts = datetime.now().strftime("%m%d_%H%M%S")
        out_dir = root / "demo_output"
        out_dir.mkdir(exist_ok=True)
        domain = args.url.replace("https://", "").replace("http://", "").split("/")[0].replace(".", "_")
        out_path = out_dir / f"{domain}_{ts}.jpg"

    print(f"\n{'='*52}")
    print(f"  YOLO ONNX 推理演示")
    print(f"{'='*52}")
    print(f"  模型:  {model_path.name}")
    print(f"  URL:   {args.url}")
    print(f"  conf:  {args.conf}")
    print()

    # Step 1: 截图
    print("[1/3] 截图...")
    img = screenshot_url(args.url, args.width, args.height)

    # Step 2: 推理
    print(f"\n[2/3] ONNX 推理...")
    results = run_onnx(img, str(model_path), conf_thresh=args.conf)
    print(f"  → 检测到 {len(results)} 个元素")
    print_summary(results)

    # Step 3: 画框并保存
    print(f"\n[3/3] 保存结果...")
    annotated = draw_results(img, results)

    # 右下角水印
    h, w = annotated.shape[:2]
    watermark = f"YOLO UI | {model_path.name} | conf>={args.conf}"
    cv2.putText(annotated, watermark, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

    cv2.imwrite(str(out_path), annotated, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"  → 已保存: {out_path}")

    if not args.no_open:
        print("  → 正在打开结果图...")
        open_image(str(out_path))

    print(f"\n  完成！\n")


if __name__ == "__main__":
    main()
