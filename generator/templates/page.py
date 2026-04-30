"""页面布局组装器 — 把各种元素拼成完整HTML页面"""
import random
from ..config import PAGE_SIZES, DARK
from .button import generate_button_html
from .input import generate_input_html, generate_checkbox_html, generate_radio_html, generate_select_html, generate_textarea_html
from .modal import generate_modal_html, generate_overlay_html, generate_link_html, generate_icon_html


def generate_page():
    """生成一页完整的HTML，返回 (html, width, height, element_meta_list)"""
    width, height = random.choice(PAGE_SIZES)
    dark_theme = random.random() < 0.2  # 20%概率暗色

    if dark_theme:
        page_bg = random.choice(DARK["bg_page"])
        text_color = random.choice(DARK["text_primary"])
    else:
        page_bg = "#ffffff"
        text_color = "#212529"

    # 决定页面类型
    page_type = random.choices(
        ["form", "mixed", "dashboard", "login"],
        weights=[0.35, 0.35, 0.2, 0.1]
    )[0]

    body_parts = []
    element_meta = []  # 记录每个元素的元信息

    if page_type == "form":
        body_parts.append(_form_layout())
    elif page_type == "mixed":
        body_parts.append(_mixed_layout())
    elif page_type == "dashboard":
        body_parts.append(_dashboard_layout())
    else:
        body_parts.append(_login_layout())

    # 解析 body_parts，提取HTML和meta
    all_html = ""
    for part in body_parts:
        if isinstance(part, tuple):
            html_str, metas = part
            all_html += html_str
            element_meta.extend(metas)
        else:
            all_html += part

    # 随机加弹窗（15%概率）
    modal_html = ""
    if random.random() < 0.15:
        modal_html, modal_meta = generate_modal_html()
        all_html += modal_html
        element_meta.append(modal_meta)

    # 随机加半透明遮罩（8%概率，但不和弹窗同时出现）
    if not modal_html and random.random() < 0.08:
        overlay_html, overlay_meta = generate_overlay_html()
        # 遮罩放在内容上方
        all_html = f'<div style="position:relative;">{all_html}{overlay_html}</div>'
        element_meta.append(overlay_meta)

    # 给每个可交互元素加 class 标记，方便后续 JS 提取
    html_page = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Synthetic UI</title></head>
<body style="margin:0;padding:24px;background:{page_bg};color:{text_color};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
{all_html}
</body>
</html>"""

    return html_page, width, height, element_meta


def _gen_element(el_type):
    """统一生成单个元素，返回 (html, meta)"""
    if el_type == "button":
        return generate_button_html()
    elif el_type == "input":
        return generate_input_html()
    elif el_type == "checkbox":
        return generate_checkbox_html()
    elif el_type == "radio":
        return generate_radio_html()
    elif el_type == "select":
        return generate_select_html()
    elif el_type == "textarea":
        return generate_textarea_html()
    elif el_type == "link":
        return generate_link_html()
    elif el_type == "icon":
        return generate_icon_html()
    else:
        return "", {"type": "unknown"}


def _random_elements(count, weights=None):
    """生成 count 个随机元素"""
    if weights is None:
        weights = {"button": 25, "input": 20, "link": 15, "icon": 12,
                   "select": 8, "checkbox": 5, "radio": 5, "textarea": 5}
    types = list(weights.keys())
    w = list(weights.values())
    html_parts = []
    metas = []
    for _ in range(count):
        t = random.choices(types, w)[0]
        h, m = _gen_element(t)
        html_parts.append(f'<div style="margin:8px;display:inline-block;vertical-align:top;">{h}</div>')
        metas.append(m)
    return "\n".join(html_parts), metas


def _form_layout():
    """表单布局：多个 label+input 纵向排列"""
    n = random.randint(4, 8)
    parts = []
    metas = []
    for _ in range(n):
        t = random.choice(["input", "input", "input", "select", "textarea", "checkbox"])
        h, m = _gen_element(t)
        parts.append(f'<div style="margin-bottom:16px;">{h}</div>')
        metas.append(m)
    # 提交按钮
    h, m = generate_button_html(disabled=False)
    parts.append(f'<div style="margin-top:8px;">{h}</div>')
    metas.append(m)
    container = f'<div style="max-width:500px;margin:0 auto;padding:24px;">{"".join(parts)}</div>'
    return container, metas


def _mixed_layout():
    """混合布局：按钮、链接、输入框混排"""
    n = random.randint(5, 10)
    parts = []
    metas = []
    for _ in range(n):
        t = random.choice(["button", "button", "input", "link", "icon", "checkbox", "select"])
        h, m = _gen_element(t)
        parts.append(f'<span style="display:inline-block;margin:6px 10px;">{h}</span>')
        metas.append(m)
    container = f'<div style="padding:24px;">{"".join(parts)}</div>'
    return container, metas


def _dashboard_layout():
    """仪表盘布局：侧边栏 + 内容区"""
    # 侧边栏
    sidebar_links = []
    for text in ["首页", "数据", "设置", "用户", "帮助"]:
        h, m = generate_link_html()
        sidebar_links.append(f'<div style="padding:8px 16px;">{h}</div>')
    sidebar = f'<div style="float:left;width:180px;min-height:500px;border-right:1px solid #dee2e6;">{"".join(sidebar_links)}</div>'

    # 内容区
    btns, metas = _random_elements(random.randint(4, 7), {"button": 30, "input": 20, "select": 15, "link": 10, "icon": 10, "checkbox": 5})
    content = f'<div style="margin-left:200px;padding:24px;"><h3 style="font-weight:500;margin-bottom:16px;">Dashboard</h3>{btns}</div>'

    return f'<div style="overflow:hidden;">{sidebar}{content}</div>', metas


def _login_layout():
    """登录页布局：居中表单"""
    h1, m1 = _gen_element("input")
    h2, m2 = _gen_element("input")
    h3, m3 = generate_button_html(disabled=False)
    h4, m4 = generate_checkbox_html()
    h5, m5 = generate_link_html()
    container = f"""
<div style="display:flex;align-items:center;justify-content:center;min-height:500px;">
  <div style="width:340px;padding:32px;border:1px solid #dee2e6;border-radius:8px;background:#fff;">
    <h2 style="text-align:center;font-weight:400;margin-bottom:24px;">Sign in</h2>
    <div style="margin-bottom:16px;">{h1}</div>
    <div style="margin-bottom:16px;">{h2}</div>
    <div style="margin-bottom:16px;">{h4}</div>
    <div style="margin-bottom:12px;">{h3}</div>
    <div style="text-align:center;">{h5}</div>
  </div>
</div>"""
    return container, [m1, m2, m3, m4, m5]
