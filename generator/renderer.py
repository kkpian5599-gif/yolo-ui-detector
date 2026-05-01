"""Playwright渲染器：打开HTML → 截图 → 提取bbox

优化项：
  #4  修复 icon 选择器（改为 <i> 标签，过滤普通文本 span）
  #5  截图后 Pillow 轻度图像增强（色调、亮度、轻微模糊）
  #8  持久化 browser / page，避免每张图冷启动
  #9  data-yolo-class 属性识别 modal/overlay
"""
import random
import tempfile
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter
from playwright.sync_api import sync_playwright, Browser, Page


# ──────────────────────────────────────────────
# JS 选择器：提取所有需要标注的元素
# 改动点 #4：明确用 i[class*="fa-"] / i[class*="bi "] 捕获字体图标，
#           移除误抓普通文本 span 的旧选择器。
# 改动点 #9：data-yolo-class="modal" 属性统一识别弹窗/遮罩。
# ──────────────────────────────────────────────
_EXTRACT_BBOXES_JS = """() => {
    const interactive = document.querySelectorAll(
        'button:not(.modal-btn-cancel):not(.modal-btn-ok), ' +
        'input:not([type="hidden"]), ' +
        'select, ' +
        'textarea, ' +
        'a, ' +
        '[data-yolo-class], ' +
        'label:has(input[type="checkbox"]), ' +
        'label:has(input[type="radio"]), ' +
        'i[class*="fa-"], ' +
        'i[class*="bi "]'
    );
    const results = [];
    const seen = new Set();

    interactive.forEach(el => {
        const rect = el.getBoundingClientRect();
        const tag  = el.tagName.toLowerCase();

        // 跳过不可见或超小元素
        if (rect.width < 5 || rect.height < 5) return;
        // 跳过视口外（允许少量溢出）
        if (rect.x < -100 || rect.y < -100) return;

        // 坐标级别去重（稍后 Python 侧再做 IoU 去重）
        const key = `${Math.round(rect.x)}_${Math.round(rect.y)}_${Math.round(rect.width)}_${Math.round(rect.height)}`;
        if (seen.has(key)) return;
        seen.add(key);

        const elType    = el.type        || '';
        const className = el.className   || '';
        const yoloClass = el.dataset.yoloClass || '';   // #9
        const text      = (el.textContent || '').trim().substring(0, 30);

        results.push({
            tag:       tag,
            type:      elType,
            text:      text,
            className: className,
            yoloClass: yoloClass,
            x: rect.x,
            y: rect.y,
            w: rect.width,
            h: rect.height
        });
    });
    return results;
}"""


# ──────────────────────────────────────────────
# Pillow 轻度增强 (#5)
# ──────────────────────────────────────────────
def _augment_image(img_path: str) -> None:
    """对截图施加随机轻度变换，提升模型鲁棒性。"""
    roll = random.random()
    if roll > 0.45:          # 约 55% 的图不做增强（保留原始干净图）
        return

    img = Image.open(img_path)

    # 色调/亮度随机微调 ±10%
    if random.random() < 0.6:
        factor = random.uniform(0.90, 1.10)
        img = ImageEnhance.Brightness(img).enhance(factor)

    # 对比度微调
    if random.random() < 0.4:
        factor = random.uniform(0.92, 1.08)
        img = ImageEnhance.Contrast(img).enhance(factor)

    # 饱和度微调
    if random.random() < 0.3:
        factor = random.uniform(0.90, 1.10)
        img = ImageEnhance.Color(img).enhance(factor)

    # 极轻微高斯模糊（模拟低分辨率截图）
    if random.random() < 0.20:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.7)))

    img.save(img_path, "JPEG", quality=92)


# ──────────────────────────────────────────────
# 持久化 Browser context (#8)
# ──────────────────────────────────────────────
class BrowserSession:
    """在整个生成流程中复用单个 Browser 实例，避免每张图冷启动。"""

    def __init__(self):
        self._pw = None
        self._browser: Browser | None = None
        self._page: Page | None = None
        self._current_size: tuple[int, int] = (0, 0)

    def start(self):
        self._pw = sync_playwright().start()
        # 优先使用 Edge（Windows），失败则 fallback 到内置 Chromium
        try:
            self._browser = self._pw.chromium.launch(channel="msedge")
        except Exception:
            self._browser = self._pw.chromium.launch()

    def stop(self):
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()

    def _ensure_page(self, width: int, height: int):
        """按需创建或复用 page，尺寸变化时重建。"""
        if self._page is None or self._current_size != (width, height):
            if self._page:
                self._page.close()
            self._page = self._browser.new_page(
                viewport={"width": width, "height": height}
            )
            self._current_size = (width, height)
        return self._page

    def render(self, html: str, width: int, height: int,
               output_dir: Path, index: int) -> tuple[str, list]:
        """渲染单张图，返回 (img_path, bboxes)。"""
        page = self._ensure_page(width, height)

        # 写临时 HTML
        tmp = tempfile.NamedTemporaryFile(
            suffix=".html", delete=False, mode="w", encoding="utf-8"
        )
        tmp.write(html)
        tmp.close()

        page.goto(f"file://{tmp.name}")
        page.wait_for_timeout(400)

        img_path = output_dir / "images" / f"{index:05d}.jpg"
        img_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(
            path=str(img_path), full_page=False, type="jpeg", quality=92
        )

        bboxes = page.evaluate(_EXTRACT_BBOXES_JS)

        Path(tmp.name).unlink(missing_ok=True)

        # 轻度图像增强 (#5)
        _augment_image(str(img_path))

        return str(img_path), bboxes


# 模块级单例（main.py 传入使用）
_session: BrowserSession | None = None


def get_session() -> BrowserSession:
    """获取/创建全局 BrowserSession 单例。"""
    global _session
    if _session is None:
        _session = BrowserSession()
        _session.start()
    return _session


def render_page(html: str, width: int, height: int,
                output_dir: Path, index: int,
                session: BrowserSession | None = None):
    """
    渲染一页HTML，返回 (截图路径, 元素bbox列表)

    session 若为 None 则使用全局单例（向后兼容旧调用方式）。
    """
    if session is None:
        session = get_session()
    return session.render(html, width, height, output_dir, index)


# ──────────────────────────────────────────────
# 类别映射
# ──────────────────────────────────────────────
def map_to_class(tag: str, el_type: str, class_name: str,
                 text: str, yolo_class: str = "") -> int:
    """将DOM元素映射到YOLO类别ID"""
    # #9 优先：data-yolo-class 属性显式指定
    if yolo_class == "modal":
        return 8

    # 旧兜底（保留兼容）
    if "modal-overlay" in class_name or "overlay-area" in class_name:
        return 8  # modal

    if tag == "button":
        return 0  # button
    elif tag == "input":
        if el_type == "checkbox":
            return 2  # checkbox
        elif el_type == "radio":
            return 3  # radio
        else:
            return 1  # input
    elif tag == "select":
        return 4  # select
    elif tag == "textarea":
        return 5  # textarea
    elif tag == "a":
        return 6  # link
    elif tag == "i":
        return 7  # icon（#4：Font Awesome / Bootstrap Icons <i> 标签）
    elif tag == "label":
        # label 包裹 checkbox/radio
        if "checkbox" in class_name or "checkbox" in str(el_type):
            return 2
        return 3
    return -1  # 不是目标类别


# ──────────────────────────────────────────────
# IoU 工具 (#1)
# ──────────────────────────────────────────────
def compute_iou(a: dict, b: dict) -> float:
    """计算两个 bbox 的 IoU（像素坐标系，x/y/w/h 格式）。"""
    ax1, ay1 = a["x"], a["y"]
    ax2, ay2 = ax1 + a["w"], ay1 + a["h"]
    bx1, by1 = b["x"], b["y"]
    bx2, by2 = bx1 + b["w"], by1 + b["h"]

    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    if inter == 0:
        return 0.0

    area_a = a["w"] * a["h"]
    area_b = b["w"] * b["h"]
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0
