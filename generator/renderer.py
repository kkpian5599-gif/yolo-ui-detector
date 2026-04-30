"""Playwright渲染器：打开HTML → 截图 → 提取bbox"""
import json
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright


def render_page(html: str, width: int, height: int, output_dir: Path, index: int):
    """
    渲染一页HTML，返回 (截图路径, 元素bbox列表)

    每个bbox: {tag, class_id, x_center_norm, y_center_norm, w_norm, h_norm}
    """
    # 写临时HTML文件
    tmp = tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8")
    tmp.write(html)
    tmp.close()
    html_path = tmp.name

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"file://{html_path}")

        # 等待渲染完成
        page.wait_for_timeout(500)

        # 截图
        img_path = output_dir / "images" / f"{index:05d}.jpg"
        img_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(img_path), full_page=False, type="jpeg", quality=92)

        # JS提取所有交互元素的bbox
        bboxes = page.evaluate("""() => {
            const interactive = document.querySelectorAll(
                'button, input:not([type="hidden"]), select, textarea, a, [class*="modal-overlay"], [class*="overlay-area"], label:has(input[type="checkbox"]), label:has(input[type="radio"]), span[style*="font-size"]:not(:has(*))'
            );
            const results = [];
            const seen = new Set();

            interactive.forEach(el => {
                const rect = el.getBoundingClientRect();
                const tag = el.tagName.toLowerCase();

                // 跳过不可见元素
                if (rect.width < 5 || rect.height < 5) return;
                // 跳过屏幕外的
                if (rect.x < -100 || rect.y < -100) return;
                // 去重（同一个元素可能被多个选择器匹配）
                const key = `${Math.round(rect.x)}_${Math.round(rect.y)}_${Math.round(rect.width)}_${Math.round(rect.height)}`;
                if (seen.has(key)) return;
                seen.add(key);

                const type = el.type || '';
                const className = el.className || '';
                const text = (el.textContent || '').trim().substring(0, 30);

                results.push({
                    tag: tag,
                    type: type,
                    text: text,
                    className: className,
                    x: rect.x,
                    y: rect.y,
                    w: rect.width,
                    h: rect.height
                });
            });
            return results;
        }""")

        browser.close()

    # 清理临时文件
    Path(html_path).unlink(missing_ok=True)

    return str(img_path), bboxes


def map_to_class(tag, el_type, class_name, text):
    """将DOM元素映射到YOLO类别ID"""
    # 先检查是否是弹窗/遮罩
    if "modal-overlay" in class_name:
        return 8  # modal
    if "overlay-area" in class_name:
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
    elif tag == "span":
        return 7  # icon
    elif tag == "label":
        # label 包裹 checkbox/radio，归类为对应控件
        if "checkbox" in class_name or "checkbox" in str(el_type):
            return 2
        return 3
    return -1  # 不是目标类别
