"""弹窗、遮罩、链接、图标生成器

P3 新增：
  generate_toast_html()  — 角落浮出通知（success/error/warning/info）
  generate_drawer_html() — 右侧抽屉面板
"""
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


# ─── P3: Toast 通知 ──────────────────────────────────────
def generate_toast_html():
    """生成角落浮出通知（success/error/warning/info）

    标注为 modal 类别：属于覆盖在主内容上的 UI 层。
    """
    variant = random.choice(["success", "error", "warning", "info"])
    position = random.choice([
        "top-right", "top-left", "bottom-right", "bottom-left", "top-center"
    ])

    # 颜色配置
    cfg = {
        "success": {"bg": "#f0fdf4", "border": "#86efac", "icon_color": "#16a34a",
                    "text": "#15803d", "icon": "✓",
                    "msgs": ["操作成功！", "保存成功", "提交成功", "Success!", "Saved successfully"]},
        "error":   {"bg": "#fef2f2", "border": "#fca5a5", "icon_color": "#dc2626",
                    "text": "#b91c1c", "icon": "✕",
                    "msgs": ["操作失败！", "网络错误", "请求超时", "Error occurred!", "Request failed"]},
        "warning": {"bg": "#fffbeb", "border": "#fcd34d", "icon_color": "#d97706",
                    "text": "#92400e", "icon": "⚠",
                    "msgs": ["请注意！", "数据未保存", "即将超时", "Warning!", "Unsaved changes"]},
        "info":    {"bg": "#eff6ff", "border": "#93c5fd", "icon_color": "#2563eb",
                    "text": "#1e40af", "icon": "ℹ",
                    "msgs": ["提示信息", "正在处理...", "请稍候", "Info", "Processing..."]},
    }[variant]

    msg = random.choice(cfg["msgs"])

    # 定位
    pos_map = {
        "top-right":    "top:20px;right:20px",
        "top-left":     "top:20px;left:20px",
        "bottom-right": "bottom:20px;right:20px",
        "bottom-left":  "bottom:20px;left:20px",
        "top-center":   "top:20px;left:50%;transform:translateX(-50%)",
    }
    pos_style = pos_map[position]

    width = random.choice([240, 280, 320])
    border_radius = random.choice([6, 8, 10, 12])

    style = (
        f"position:fixed;{pos_style};"
        f"min-width:{width}px;max-width:360px;"
        f"background:{cfg['bg']};"
        f"border:1px solid {cfg['border']};"
        f"border-radius:{border_radius}px;"
        f"padding:12px 16px;"
        f"display:flex;align-items:flex-start;gap:10px;"
        f"box-shadow:0 4px 12px rgba(0,0,0,0.10);"
        f"z-index:1100;"
        f"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
    )
    icon_style = (
        f"font-size:16px;color:{cfg['icon_color']};"
        f"font-weight:700;flex-shrink:0;margin-top:1px;"
    )
    text_style = f"font-size:14px;color:{cfg['text']};line-height:1.4;"

    html = (
        f'<div style="{style}" data-yolo-class="modal" class="toast-notification">'
        f'  <span style="{icon_style}">{cfg["icon"]}</span>'
        f'  <span style="{text_style}">{msg}</span>'
        f'</div>'
    )
    return html, {"type": "toast", "variant": variant, "position": position}


# ─── P3: Drawer 抽屉面板 ─────────────────────────────────
def generate_drawer_html():
    """生成右侧抽屉面板（侧边弹出，有标题、内容、底部按钮）

    标注为 modal 类别：属于覆盖在主内容上的 UI 层。
    抽屉内的 button/input 同样会被 JS 选择器捕获，标注为对应类别。
    """
    from .button import generate_button_html
    from .input import generate_input_html, generate_select_html

    dark = random.random() < 0.2
    bg   = random.choice(["#1e1e2e", "#1f2937", "#111827"]) if dark else random.choice(["#ffffff", "#f8f9fa", "#fafafa"])
    text = "#e5e7eb" if dark else "#212529"
    border_c = "#374151" if dark else "#e5e7eb"

    title = random.choice(["编辑信息", "筛选条件", "详情", "设置", "Edit", "Filter", "Details", "Settings"])
    width = random.choice([320, 360, 400, 440])

    # 遮罩
    overlay_style = (
        "position:fixed;top:0;left:0;right:0;bottom:0;"
        "background:rgba(0,0,0,0.40);z-index:1000;"
        "display:flex;justify-content:flex-end;"
    )
    # 面板
    panel_style = (
        f"width:{width}px;height:100%;"
        f"background:{bg};color:{text};"
        f"display:flex;flex-direction:column;"
        f"box-shadow:-4px 0 20px rgba(0,0,0,0.15);"
        f"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
    )
    header_style = (
        f"display:flex;align-items:center;justify-content:space-between;"
        f"padding:16px 20px;border-bottom:1px solid {border_c};"
        f"font-size:16px;font-weight:600;"
    )
    body_style = "flex:1;overflow-y:auto;padding:20px;"
    footer_style = (
        f"padding:16px 20px;border-top:1px solid {border_c};"
        f"display:flex;justify-content:flex-end;gap:8px;"
    )

    # 抽屉内放 1-3 个输入元素
    n_fields = random.randint(1, 3)
    fields_html = ""
    for _ in range(n_fields):
        t = random.choice(["input", "input", "select"])
        if t == "input":
            h, _ = generate_input_html()
        else:
            h, _ = generate_select_html()
        fields_html += f'<div style="margin-bottom:16px;">{h}</div>'

    btn_ok_html, _ = generate_button_html(disabled=False)
    btn_cancel_text = random.choice(["取消", "关闭", "Cancel"])
    btn_cancel_style = (
        "padding:6px 16px;font-size:14px;border-radius:4px;cursor:pointer;"
        f"background:transparent;color:{text};border:1px solid {border_c};"
    )

    html = f"""
<div style="{overlay_style}" data-yolo-class="modal" class="drawer-overlay">
  <div style="{panel_style}" class="drawer-panel">
    <div style="{header_style}">
      <span>{title}</span>
      <button style="background:none;border:none;font-size:18px;cursor:pointer;color:{text};">✕</button>
    </div>
    <div style="{body_style}">
      {fields_html}
    </div>
    <div style="{footer_style}">
      <button style="{btn_cancel_style}">{btn_cancel_text}</button>
      {btn_ok_html}
    </div>
  </div>
</div>"""
    return html, {"type": "drawer", "dark": dark, "width": width}
