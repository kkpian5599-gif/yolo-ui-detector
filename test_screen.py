# -*- coding: utf-8 -*-
import sys, io
# Windows GBK 终端强制 UTF-8 输出
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
"""
实时截图 + ONNX 识别测试
用法:
    python test_screen.py              # 截全屏识别
    python test_screen.py --file x.png # 识别指定图片
    python test_screen.py --loop       # 每5秒截图一次，持续识别
"""
import argparse
import time
from pathlib import Path

import cv2
import numpy as np

# ── 配置 ────────────────────────────────────────────
MODEL_PATH = Path(__file__).parent / "best.onnx"
OUTPUT_DIR = Path(__file__).parent / "test_output"
OUTPUT_DIR.mkdir(exist_ok=True)

CLASSES = ["button", "input", "checkbox", "radio", "select",
           "textarea", "link", "icon", "modal"]

# 每个类别一个颜色（BGR）
COLORS = {
    "button":   (  0, 200, 255),   # 橙
    "input":    (  0, 255, 100),   # 绿
    "checkbox": (255, 100,   0),   # 蓝
    "radio":    (255,   0, 200),   # 紫
    "select":   (  0, 200, 200),   # 青
    "textarea": (100, 255,   0),   # 黄绿
    "link":     (255, 200,   0),   # 天蓝
    "icon":     (200,   0, 255),   # 粉紫
    "modal":    (  0,   0, 255),   # 红
}

CONF_THRESH = 0.4  # 置信度阈值（降低可看到更多框）
NMS_THRESH  = 0.45

# ── 加载模型 ─────────────────────────────────────────
print(f"加载 ONNX 模型: {MODEL_PATH}")
net = cv2.dnn.readNet(str(MODEL_PATH))
print("[OK] 模型加载完成\n")


def take_screenshot() -> np.ndarray:
    """截取全屏，返回 BGR numpy 数组"""
    try:
        import mss
        with mss.MSS() as sct:
            monitor = sct.monitors[0]  # 全屏（含多显示器用 [1] 只取主屏）
            shot = sct.grab(monitor)
            img = np.array(shot)
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    except ImportError:
        pass

    try:
        import pyautogui
        shot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    except ImportError:
        pass

    raise RuntimeError("请安装截图库：pip install mss 或 pip install pyautogui")


def detect(img: np.ndarray) -> list[dict]:
    """运行 ONNX 推理，返回检测结果列表"""
    h, w = img.shape[:2]

    blob = cv2.dnn.blobFromImage(img, 1/255.0, (640, 640), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward()   # shape: (1, 13, 8400)
    preds = outputs[0]        # (13, 8400)  — 4 bbox + 9 classes

    boxes, scores, class_ids = [], [], []

    for i in range(preds.shape[1]):
        cls_scores = preds[4:, i]
        max_score = float(np.max(cls_scores))
        if max_score < CONF_THRESH:
            continue
        max_cls = int(np.argmax(cls_scores))

        cx, cy, bw, bh = preds[0:4, i]
        # 还原到原图坐标
        cx = cx * w / 640
        cy = cy * h / 640
        bw = bw * w / 640
        bh = bh * h / 640

        x1 = int(cx - bw / 2)
        y1 = int(cy - bh / 2)

        boxes.append([x1, y1, int(bw), int(bh)])
        scores.append(max_score)
        class_ids.append(max_cls)

    results = []
    if not boxes:
        return results

    indices = cv2.dnn.NMSBoxes(boxes, scores, CONF_THRESH, NMS_THRESH)
    if len(indices) == 0:
        return results

    for idx in indices.flatten():
        x1, y1, bw, bh = boxes[idx]
        cls = CLASSES[class_ids[idx]]
        results.append({
            "class": cls,
            "conf":  scores[idx],
            "bbox":  (x1, y1, x1 + bw, y1 + bh),
        })

    return results


def draw_results(img: np.ndarray, results: list[dict]) -> np.ndarray:
    """在图上绘制检测框和标签"""
    vis = img.copy()
    for r in results:
        cls  = r["class"]
        conf = r["conf"]
        x1, y1, x2, y2 = r["bbox"]
        color = COLORS.get(cls, (0, 255, 0))
        label = f"{cls} {conf:.0%}"

        cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)

        # 标签背景
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        ly = max(y1 - 4, th + 4)
        cv2.rectangle(vis, (x1, ly - th - 4), (x1 + tw + 4, ly), color, -1)
        cv2.putText(vis, label, (x1 + 2, ly - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)

    return vis


def print_summary(results: list[dict], elapsed_ms: float):
    """打印控制台汇总"""
    from collections import Counter
    counts = Counter(r["class"] for r in results)

    print(f"\n{'─'*50}")
    print(f"  识别到 {len(results)} 个 UI 元素  ({elapsed_ms:.0f}ms)")
    print(f"{'─'*50}")
    for cls in CLASSES:
        n = counts.get(cls, 0)
        if n > 0:
            confs = [r["conf"] for r in results if r["class"] == cls]
            avg = sum(confs) / len(confs)
            bar = "█" * n
            print(f"  {cls:<10} {bar:<20} {n:>3} 个  (avg {avg:.0%})")
    print(f"{'─'*50}\n")


def run_once(img_path: str | None = None, save_suffix: str = ""):
    if img_path:
        img = cv2.imread(img_path)
        if img is None:
            raise FileNotFoundError(f"找不到图片: {img_path}")
        print(f"读取图片: {img_path}")
    else:
        print("截取屏幕中...")
        img = take_screenshot()
        print(f"  截图尺寸: {img.shape[1]}x{img.shape[0]}")

    t0 = time.perf_counter()
    results = detect(img)
    elapsed = (time.perf_counter() - t0) * 1000

    print_summary(results, elapsed)

    vis = draw_results(img, results)
    ts = time.strftime("%H%M%S")
    out_path = OUTPUT_DIR / f"screen_{ts}{save_suffix}.jpg"
    cv2.imwrite(str(out_path), vis)
    print(f"  结果图保存: {out_path}")

    # 用系统默认看图软件打开（Windows 用 os.startfile，兼容无 GUI 的 OpenCV）
    import os, platform
    if platform.system() == "Windows":
        os.startfile(str(out_path))
    elif platform.system() == "Darwin":
        os.system(f'open "{out_path}"')
    else:
        os.system(f'xdg-open "{out_path}"')


def run_loop(interval: int = 5):
    print(f"持续模式：每 {interval} 秒截图一次，按 Ctrl+C 退出\n")
    i = 0
    try:
        while True:
            run_once(save_suffix=f"_{i:03d}")
            i += 1
            print(f"等待 {interval} 秒... (Ctrl+C 退出)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n已退出。")


def run_interactive():
    """交互模式：回车截图，q+回车退出"""
    print("=" * 52)
    print("  交互模式：打开任意网页后按 Enter 截图识别")
    print("  输入 q 然后回车退出")
    print("=" * 52)
    i = 0
    while True:
        try:
            cmd = input(f"\n[第{i+1}次] 按 Enter 截图，或输入 q 退出 > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            break
        if cmd == "q":
            print("已退出。")
            break
        note = input("  备注（当前页面名称，可留空）> ").strip()
        suffix = f"_{i:03d}_{note.replace(' ','_')}" if note else f"_{i:03d}"
        run_once(save_suffix=suffix)
        i += 1


# ── 入口 ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YOLO UI 检测器 - 截图测试")
    parser.add_argument("--file",        type=str,            default=None, help="指定图片路径")
    parser.add_argument("--loop",        action="store_true",               help="定时循环截图")
    parser.add_argument("--interactive", action="store_true",               help="交互式：按Enter截图")
    parser.add_argument("--interval",    type=int,            default=5,    help="loop 间隔秒数")
    parser.add_argument("--conf",        type=float,          default=0.4,  help="置信度阈值（默认0.4）")
    args = parser.parse_args()

    CONF_THRESH = args.conf

    if args.interactive:
        run_interactive()
    elif args.loop:
        run_loop(args.interval)
    else:
        run_once(img_path=args.file)
