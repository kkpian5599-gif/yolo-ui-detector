"""弹窗、遮罩、链接、图标生成器"""
import random
from ..config import STYLE_PROFILE, LINK_TEXTS

MDL = STYLE_PROFILE["modals_and_overlays"]
DARK = STYLE_PROFILE["dark_theme"]


def generate_modal_html():
    """生成弹窗（居中白色卡片 + 半透明遮罩）"""
    dark = random.random() < 0.2
    overlay_color = random.choice(MDL["backdrop"]["colors"])
    modal_bg = MDL["modal_dark"]["bg"] if dark else MDL["modal_card"]["bg"]
    title_text = random.choice(["提示", "确认操作", "删除确认", "信息", "温馨提示", "Confirm", "Alert"])
    body_text = random.choice([
        "确定要执行此操作吗？", "操作成功！", "是否确认删除该条记录？",
        "Are you sure?", "Operation successful!", "Please confirm."
    ])
    btn_ok = random.choice(["确定", "确认", "OK", "Confirm"])
    btn_cancel = random.choice(["取消", "关闭", "Cancel", "Close"])

    overlay_style = (
        f"position:fixed;top:0;left:0;right:0;bottom:0;"
        f"background:{overlay_color};"
        f"display:flex;align-items:center;justify-content:center;"
        f"z-index:1000;"
    )
    modal_style = (
        f"background:{modal_bg};"
        f"border-radius:8px;"
        f"box-shadow:0 4px 24px rgba(0,0,0,0.15);"
        f"padding:24px;"
        f"min-width:320px;max-width:480px;"
    )
    title_style = "font-size:16px;font-weight:600;margin-bottom:12px;color:#212529;font-family:-apple-system,BlinkMacSystemFont,sans-serif;"
    body_style = "font-size:14px;color:#666;margin-bottom:20px;font-family:-apple-system,BlinkMacSystemFont,sans-serif;"
    btn_style = (
        "display:inline-block;padding:6px 16px;font-size:14px;border-radius:4px;cursor:pointer;"
        "font-family:-apple-system,BlinkMacSystemFont,sans-serif;margin-left:8px;"
    )
    btn_ok_style = f"{btn_style}background:#0d6efd;color:#fff;border:1px solid #0d6efd;"
    btn_cancel_style = f"{btn_style}background:#fff;color:#606266;border:1px solid #dcdfe6;"

    html = f"""
<div style="{overlay_style}" class="modal-overlay" data-yolo-class="modal">
  <div style="{modal_style}" class="modal-card">
    <div style="{title_style}">{title_text}</div>
    <div style="{body_style}">{body_text}</div>
    <div style="text-align:right;">
      <button class="modal-btn-cancel" style="{btn_cancel_style}">{btn_cancel}</button>
      <button class="modal-btn-ok" style="{btn_ok_style}">{btn_ok}</button>
    </div>
  </div>
</div>"""
    return html, {"type": "modal", "dark": dark, "title": title_text}


def generate_overlay_html():
    """生成半透明遮罩（模拟 loading 或 backdrop）"""
    opacity = random.choice([0.3, 0.4, 0.5, 0.6])
    color = random.choice(["0,0,0", "255,255,255"])
    style = (
        f"position:absolute;top:0;left:0;right:0;bottom:0;"
        f"background:rgba({color},{opacity});"
        f"z-index:900;"
        # 给个虚边框让YOLO更容易识别
        f"border:2px dashed rgba(128,128,128,0.3);"
    )
    html = f'<div style="{style}" class="overlay-area" data-yolo-class="modal"></div>'
    return html, {"type": "overlay", "opacity": opacity}


def generate_link_html():
    """生成超链接"""
    color = random.choice(["#0d6efd", "#0969da", "#409eff", "#59636e"])
    text = random.choice(LINK_TEXTS)
    fs = random.choice(["12px", "14px", "16px"])
    style = (
        f"color:{color};font-size:{fs};text-decoration:{random.choice(['none','underline'])};"
        f"cursor:pointer;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
    )
    href = random.choice(["#", "javascript:void(0)", "https://example.com"])
    html = f'<a href="{href}" style="{style}">{text}</a>'
    return html, {"type": "link", "text": text}


def generate_icon_html():
    """生成独立图标（Font Awesome <i> 标签，可被 renderer 正确捕获）"""
    # 图标名称 -> FA class
    icons = [
        "fa-solid fa-magnifying-glass",
        "fa-solid fa-gear",
        "fa-solid fa-house",
        "fa-solid fa-folder",
        "fa-solid fa-star",
        "fa-solid fa-heart",
        "fa-solid fa-pencil",
        "fa-solid fa-trash",
        "fa-solid fa-envelope",
        "fa-solid fa-bell",
        "fa-solid fa-user",
        "fa-solid fa-clipboard",
        "fa-solid fa-clock",
        "fa-solid fa-floppy-disk",
        "fa-solid fa-circle-plus",
        "fa-solid fa-circle-xmark",
        "fa-solid fa-upload",
        "fa-solid fa-download",
        "fa-solid fa-share-nodes",
        "fa-solid fa-filter",
        "fa-solid fa-bars",
        "fa-solid fa-ellipsis",
        "fa-solid fa-lock",
        "fa-solid fa-key",
        "fa-solid fa-globe",
        "fa-solid fa-chart-bar",
        "fa-solid fa-table-columns",
        "fa-solid fa-image",
        "fa-solid fa-file-text",
        "fa-solid fa-link",
    ]
    icon_cls = random.choice(icons)
    size = random.choice(["16px", "18px", "20px", "24px", "28px", "32px"])
    color = random.choice([
        "#6c757d", "#0d6efd", "#198754", "#dc3545", "#ffc107",
        "#0dcaf0", "#6f42c1", "#fd7e14", "#20c997", "#212529",
    ])
    style = f"display:inline-block;font-size:{size};color:{color};line-height:1;"
    html = f'<i class="{icon_cls}" style="{style}"></i>'
    return html, {"type": "icon", "cls": icon_cls, "size": size}
