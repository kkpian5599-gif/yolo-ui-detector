"""页面布局组装器 — 把各种元素拼成完整HTML页面"""
import random
from ..config import PAGE_SIZES, PAGE_SIZE_WEIGHTS, DARK, ROOT
from .button import generate_button_html
from .input import generate_input_html, generate_checkbox_html, generate_radio_html, generate_select_html, generate_textarea_html
from .modal import generate_modal_html, generate_overlay_html, generate_link_html, generate_icon_html

# 本地图标库路径（file:// 供 Playwright 离线渲染）
_STATIC = ROOT / "generator" / "static"
_FA_CSS = (_STATIC / "fontawesome" / "css" / "all.min.css").as_posix()
_BI_CSS = (_STATIC / "bootstrap-icons" / "font" / "bootstrap-icons.min.css").as_posix()



def generate_page():
    """生成一页完整的HTML，返回 (html, width, height, element_meta_list)"""
    width, height = random.choices(PAGE_SIZES, weights=PAGE_SIZE_WEIGHTS)[0]
    bg_theme = random.choices([
        "white", "light_gray", "light_color", "gradient_light",
        "gradient_vivid", "dark_solid", "dark_gradient",
        "cyber_dark", "tech_pattern", "glass_frosted",
        "warm_neutral", "brand_color",
    ], weights=[10, 10, 10, 12, 8, 10, 8, 5, 5, 5, 8, 7])[0]

    extra_body_style = ""

    if bg_theme == "white":
        page_bg = "#ffffff"
        text_color = "#212529"

    elif bg_theme == "light_gray":
        page_bg = random.choice(["#f8f9fa", "#f5f5f5", "#f0f2f5", "#f2f4f7", "#fafafa", "#f7f8fc"])
        text_color = "#212529"

    elif bg_theme == "light_color":
        page_bg = random.choice(["#eff6ff", "#f0fdf4", "#faf5ff", "#fff7ed",
                                  "#fdf2f8", "#ecfdf5", "#f0f9ff", "#fefce8"])
        text_color = "#1e293b"

    elif bg_theme == "gradient_light":
        grads = [
            ("135deg", "#e0e7ff", "#f0fdf4"),
            ("135deg", "#fce7f3", "#ede9fe"),
            ("135deg", "#fff1f2", "#fef9c3"),
            ("135deg", "#e0f2fe", "#f0fdf4"),
            ("to bottom", "#f8fafc", "#e2e8f0"),
            ("135deg", "#fdf4ff", "#eff6ff"),
            ("135deg", "#fff7ed", "#fefce8"),
        ]
        deg, c1, c2 = random.choice(grads)
        page_bg = f"linear-gradient({deg},{c1},{c2})"
        text_color = "#1e293b"

    elif bg_theme == "gradient_vivid":
        grads = [
            ("#667eea", "#764ba2"),
            ("#f093fb", "#f5576c"),
            ("#4facfe", "#00f2fe"),
            ("#43e97b", "#38f9d7"),
            ("#fa709a", "#fee140"),
            ("#a18cd1", "#fbc2eb"),
            ("#a1c4fd", "#c2e9fb"),
            ("#6a11cb", "#2575fc"),
            ("#f83600", "#f9d423"),
            ("#0f3460", "#e94560"),
        ]
        c1, c2 = random.choice(grads)
        page_bg = f"linear-gradient(135deg,{c1},{c2})"
        text_color = "#ffffff"

    elif bg_theme == "dark_solid":
        page_bg = random.choice(["#1a1a2e", "#0f172a", "#111827", "#1e1e2e",
                                  "#0d1117", "#161b22", "#1c1c1c", "#18181b",
                                  "#0f0f0f", "#1a1a1a", "#212121", "#141414"])
        text_color = random.choice(["#e2e8f0", "#f1f5f9", "#d1d5db", "#e5e7eb", "#cdd9e5"])

    elif bg_theme == "dark_gradient":
        grads = [
            ("#0f172a", "#1e293b"),
            ("#1a1a2e", "#16213e"),
            ("#0d1117", "#161b22"),
            ("#111827", "#1f2937"),
            ("#0f0f0f", "#1a1a2e"),
        ]
        c1, c2 = random.choice(grads)
        page_bg = f"linear-gradient(135deg,{c1},{c2})"
        text_color = random.choice(["#e2e8f0", "#f1f5f9", "#cdd9e5"])

    elif bg_theme == "cyber_dark":
        page_bg = random.choice(["#0a0010", "#000d1a", "#0a0a0a", "#001a0d"])
        text_color = random.choice(["#00ff41", "#00cfff", "#ff2d78", "#bf5fff", "#ffd700"])
        gc = text_color + "22"
        extra_body_style = (
            f"background-image:linear-gradient({gc} 1px,transparent 1px),"
            f"linear-gradient(90deg,{gc} 1px,transparent 1px);"
            f"background-size:40px 40px;"
        )

    elif bg_theme == "tech_pattern":
        page_bg = random.choice(["#0f172a", "#1a1a2e", "#111827", "#0d1117"])
        dc = random.choice(["#334155", "#1e3a5f", "#1e293b"])
        pt = random.choice(["dots", "grid", "diagonal"])
        if pt == "dots":
            extra_body_style = f"background-image:radial-gradient({dc} 1px,transparent 1px);background-size:24px 24px;"
        elif pt == "grid":
            extra_body_style = (
                f"background-image:linear-gradient({dc} 1px,transparent 1px),"
                f"linear-gradient(90deg,{dc} 1px,transparent 1px);"
                f"background-size:32px 32px;"
            )
        else:
            extra_body_style = (
                f"background-image:repeating-linear-gradient("
                f"45deg,{dc} 0,{dc} 1px,transparent 0,transparent 50%);"
                f"background-size:20px 20px;"
            )
        text_color = "#94a3b8"

    elif bg_theme == "glass_frosted":
        grads = [("#667eea", "#764ba2"), ("#4facfe", "#00f2fe"),
                 ("#43e97b", "#38f9d7"), ("#f093fb", "#f5576c"),
                 ("#a18cd1", "#fbc2eb")]
        c1, c2 = random.choice(grads)
        page_bg = f"linear-gradient(135deg,{c1},{c2})"
        text_color = "#ffffff"

    elif bg_theme == "warm_neutral":
        page_bg = random.choice(["#fdf6e3", "#fef3c7", "#fff8f1", "#fdf4e7", "#faf0e6", "#fdebd0"])
        text_color = "#374151"

    elif bg_theme == "brand_color":
        combos = [("#e8f0fe", "#1e3a5f"), ("#d1fae5", "#064e3b"), ("#ede9fe", "#4c1d95"),
                  ("#fef3c7", "#78350f"), ("#fdf2f8", "#831843"), ("#e0f2fe", "#0c4a6e")]
        page_bg, text_color = random.choice(combos)

    else:
        page_bg = "#ffffff"
        text_color = "#212529"

    body_style = (
        f"margin:0;padding:24px;background:{page_bg};"
        f"color:{text_color};"
        f"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
        f"min-height:100vh;{extra_body_style}"
    )

    # 决定页面类型
    page_type = random.choices(
        ["form", "mixed", "dashboard", "login", "textarea_focus"],
        weights=[0.28, 0.22, 0.15, 0.15, 0.20]
    )[0]

    body_parts = []
    element_meta = []  # 记录每个元素的元信息

    if page_type == "form":
        body_parts.append(_form_layout())
    elif page_type == "mixed":
        body_parts.append(_mixed_layout())
    elif page_type == "dashboard":
        body_parts.append(_dashboard_layout())
    elif page_type == "textarea_focus":
        body_parts.append(_textarea_focus_layout())
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

    # 随机选图标库（70% FA，30% Bootstrap Icons）
    icon_lib = random.choices(["fa", "bi"], weights=[70, 30])[0]
    if icon_lib == "fa":
        icon_css = f'<link rel="stylesheet" href="file:///{_FA_CSS}">'
    else:
        icon_css = f'<link rel="stylesheet" href="file:///{_BI_CSS}">'
    # 给每个可交互元素加 class 标记，方便后续 JS 提取
    html_page = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Synthetic UI</title>
  {icon_css}
</head>
<body style="{body_style}">
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
        weights = {"button": 20, "input": 18, "link": 12, "icon": 10,
                   "select": 8, "checkbox": 5, "radio": 5, "textarea": 22}
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


def _textarea_focus_layout():
    """textarea密集页面：专门生成多个不同样式textarea，覆盖评论区/反馈/搜索框/编辑器等场景"""
    layout_variant = random.choice([
        "feedback_form",    # 反馈表单（多个textarea）
        "comment_section",  # 评论区（多个评论框）
        "search_page",      # 搜索页（搜索框为主）
        "editor_page",      # 编辑器页面
        "contact_form",     # 联系我们表单
        "mixed_inputs",     # input+textarea混合
    ])

    parts = []
    metas = []

    if layout_variant == "feedback_form":
        title = random.choice(["意见反馈", "用户反馈", "问题反馈", "Feedback", "Submit Feedback"])
        parts.append(f'<h2 style="font-weight:500;margin-bottom:24px;font-size:20px;">{title}</h2>')
        n_ta = random.randint(2, 5)
        for _ in range(n_ta):
            h, m = generate_textarea_html()
            parts.append(f'<div style="margin-bottom:20px;">{h}</div>')
            metas.append(m)
        # 加一个提交按钮
        hb, mb = generate_button_html(disabled=False)
        parts.append(f'<div style="margin-top:8px;">{hb}</div>')
        metas.append(mb)
        container = f'<div style="max-width:600px;margin:0 auto;padding:32px;">{"" .join(parts)}</div>'

    elif layout_variant == "comment_section":
        title = random.choice(["评论区", "用户评论", "Comments", "Reviews"])
        parts.append(f'<h3 style="font-weight:500;margin-bottom:16px;">{title}</h3>')
        # 主评论框
        h, m = generate_textarea_html()
        parts.append(f'<div style="margin-bottom:16px;">{h}</div>')
        metas.append(m)
        hb, mb = generate_button_html(disabled=False)
        parts.append(f'<div style="margin-bottom:24px;">{hb}</div>')
        metas.append(mb)
        # 已有评论（1-3个，带textarea回复框）
        for _ in range(random.randint(1, 3)):
            h2, m2 = generate_textarea_html()
            parts.append(f'<div style="border-left:3px solid #e0e0e0;padding-left:16px;margin-bottom:16px;">{h2}</div>')
            metas.append(m2)
        container = f'<div style="max-width:700px;padding:24px;">{"" .join(parts)}</div>'

    elif layout_variant == "search_page":
        title = random.choice(["搜索", "全局搜索", "Search", "Find"])
        parts.append(f'<h2 style="text-align:center;font-weight:400;margin-bottom:32px;font-size:24px;">{title}</h2>')
        # 主搜索框（大圆角）
        for _ in range(random.randint(1, 3)):
            h, m = generate_textarea_html()
            parts.append(f'<div style="text-align:center;margin-bottom:20px;">{h}</div>')
            metas.append(m)
        hb, mb = generate_button_html(disabled=False)
        parts.append(f'<div style="text-align:center;margin-top:16px;">{hb}</div>')
        metas.append(mb)
        container = f'<div style="max-width:800px;margin:60px auto;padding:24px;">{"" .join(parts)}</div>'

    elif layout_variant == "editor_page":
        # 大型编辑器页面
        title = random.choice(["文章编辑", "内容编辑", "Edit", "Write", "Compose"])
        parts.append(f'<h3 style="font-weight:500;margin-bottom:12px;">{title}</h3>')
        h, m = generate_textarea_html()
        parts.append(f'<div style="margin-bottom:16px;">{h}</div>')
        metas.append(m)
        # 也许加个摘要textarea
        if random.random() < 0.6:
            h2, m2 = generate_textarea_html()
            parts.append(f'<div style="margin-bottom:12px;">{h2}</div>')
            metas.append(m2)
        hb, mb = generate_button_html(disabled=False)
        parts.append(f'<div>{hb}</div>')
        metas.append(mb)
        container = f'<div style="max-width:900px;padding:24px;">{"" .join(parts)}</div>'

    elif layout_variant == "contact_form":
        title = random.choice(["联系我们", "Contact Us", "Get in Touch", "发送消息"])
        parts.append(f'<h2 style="font-weight:500;margin-bottom:20px;">{title}</h2>')
        # name + email input
        hi1, mi1 = generate_input_html()
        hi2, mi2 = generate_input_html()
        parts.append(f'<div style="margin-bottom:12px;">{hi1}</div>')
        parts.append(f'<div style="margin-bottom:12px;">{hi2}</div>')
        metas.extend([mi1, mi2])
        # textarea for message
        n_ta = random.randint(1, 3)
        for _ in range(n_ta):
            h, m = generate_textarea_html()
            parts.append(f'<div style="margin-bottom:16px;">{h}</div>')
            metas.append(m)
        hb, mb = generate_button_html(disabled=False)
        parts.append(f'<div>{hb}</div>')
        metas.append(mb)
        container = f'<div style="max-width:560px;margin:0 auto;padding:32px;">{"" .join(parts)}</div>'

    else:  # mixed_inputs
        # 混合：textarea 权重大
        n = random.randint(4, 8)
        for _ in range(n):
            el_type = random.choices(
                ["textarea", "textarea", "input", "select", "button"],
                weights=[40, 30, 15, 8, 7]
            )[0]
            if el_type == "textarea":
                h, m = generate_textarea_html()
            elif el_type == "input":
                h, m = generate_input_html()
            elif el_type == "select":
                h, m = generate_select_html()
            else:
                h, m = generate_button_html()
            parts.append(f'<div style="margin-bottom:16px;display:inline-block;margin-right:16px;vertical-align:top;">{h}</div>')
            metas.append(m)
        container = f'<div style="padding:24px;">{"" .join(parts)}</div>'

    return container, metas
