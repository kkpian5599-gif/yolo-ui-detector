"""页面布局组装器 — 把各种元素拼成完整HTML页面

P3 新增：
  _table_layout()  — 带 checkbox 的数据表格页面
  _navbar_layout() — 横向导航栏 + 内容区
  toast 注入（5% 概率，与 modal 互斥）
  drawer 注入（8% 概率，与 modal 互斥）
"""
import random
from ..config import PAGE_SIZES, PAGE_SIZE_WEIGHTS, DARK, ROOT, RANKING_TITLES
from .button import generate_button_html
from .input import generate_input_html, generate_checkbox_html, generate_radio_html, generate_select_html, generate_textarea_html
from .modal import (
    generate_modal_html, generate_overlay_html,
    generate_link_html, generate_icon_html,
    generate_toast_html, generate_drawer_html,   # P3
)

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

    # 决定页面类型（P3：新增 table、navbar）
    page_type = random.choices(
        ["form", "mixed", "dashboard", "login", "textarea_focus", "icon_grid",
         "table", "navbar", "ranking_list", "news_feed", "social_card"],
        weights=[0.18, 0.15, 0.08, 0.10, 0.13, 0.08, 0.06, 0.04, 0.07, 0.07, 0.04]
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
    elif page_type == "icon_grid":
        body_parts.append(_icon_grid_layout())
    elif page_type == "table":
        body_parts.append(_table_layout())
    elif page_type == "navbar":
        body_parts.append(_navbar_layout())
    elif page_type == "ranking_list":
        body_parts.append(_ranking_list_layout())
    elif page_type == "news_feed":
        body_parts.append(_news_feed_layout())
    elif page_type == "social_card":
        body_parts.append(_social_card_layout())
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

    # 随机加弹窗（22%概率，提升 modal 类别覆盖）
    overlay_used = False
    modal_html = ""
    if random.random() < 0.22:
        modal_html, modal_meta = generate_modal_html()
        all_html += modal_html
        element_meta.append(modal_meta)
        overlay_used = True

    # 随机加 Drawer 抽屉（8%概率，与弹窗互斥）
    if not overlay_used and random.random() < 0.08:
        drawer_html, drawer_meta = generate_drawer_html()
        all_html += drawer_html
        element_meta.append(drawer_meta)
        overlay_used = True

    # 随机加半透明遮罩（6%概率，与弹窗/抽屉互斥）
    if not overlay_used and random.random() < 0.06:
        ov_html, ov_meta = generate_overlay_html()
        all_html = f'<div style="position:relative;">{all_html}{ov_html}</div>'
        element_meta.append(ov_meta)
        overlay_used = True

    # 随机加 Toast 通知（5%概率，可与弹窗并存——真实场景也会同时出现）
    if random.random() < 0.05:
        toast_html, toast_meta = generate_toast_html()
        all_html += toast_html
        element_meta.append(toast_meta)

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


def _icon_grid_layout():
    """图标网格布局：生成大量独立图标样本。"""
    count = random.randint(12, 28)
    parts = []
    metas = []
    for _ in range(count):
        h, m = generate_icon_html()
        tile_bg = random.choice(["#ffffff", "#f8f9fa", "#f1f5f9", "rgba(255,255,255,0.72)"])
        border = random.choice(["#dee2e6", "#e5e7eb", "#d0d7de", "rgba(0,0,0,0.08)"])
        tile_size = random.choice([44, 48, 52, 56, 64])
        parts.append(
            f'<div style="display:inline-flex;align-items:center;justify-content:center;'
            f'width:{tile_size}px;height:{tile_size}px;margin:8px;'
            f'border:1px solid {border};border-radius:8px;background:{tile_bg};'
            f'box-sizing:border-box;vertical-align:top;">{h}</div>'
        )
        metas.append(m)

    container = f'<div style="max-width:760px;margin:0 auto;padding:24px;">{"".join(parts)}</div>'
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


# ─── P3: 数据表格布局 ────────────────────────────────────
def _table_layout():
    """带 checkbox 的数据表格页面（模拟后台管理系统列表）"""
    dark = random.random() < 0.3
    bg        = random.choice(["#1e1e2e", "#0f172a", "#111827"]) if dark else "#ffffff"
    text_c    = "#e2e8f0" if dark else "#212529"
    border_c  = "#374151" if dark else "#dee2e6"
    header_bg = random.choice(["#1e293b", "#0f172a"]) if dark else random.choice(["#f8f9fa", "#f0f2f5"])
    row_hover = "rgba(255,255,255,0.05)" if dark else "#f8f9fa"
    stripe_bg = "rgba(255,255,255,0.03)" if dark else "#fafafa"

    # 列定义
    col_configs = [
        ["姓名", "邮箱", "角色", "状态", "操作"],
        ["商品名", "价格", "库存", "分类", "操作"],
        ["Name", "Email", "Department", "Status", "Actions"],
        ["订单号", "客户", "金额", "时间", "状态"],
        ["ID", "Title", "Author", "Date", "Actions"],
    ]
    cols = random.choice(col_configs)

    # 工具栏（搜索 + 按钮）
    toolbar_parts = []
    toolbar_metas = []
    h_search, m_search = generate_input_html()
    toolbar_parts.append(f'<div style="display:inline-block;margin-right:8px;">{h_search}</div>')
    toolbar_metas.append(m_search)
    for _ in range(random.randint(1, 3)):
        h_btn, m_btn = generate_button_html()
        toolbar_parts.append(f'<div style="display:inline-block;margin-right:6px;">{h_btn}</div>')
        toolbar_metas.append(m_btn)
    toolbar_html = (
        f'<div style="margin-bottom:16px;display:flex;align-items:center;gap:8px;">'
        f'{"".join(toolbar_parts)}</div>'
    )

    # 表头
    th_style = (
        f"padding:10px 14px;text-align:left;font-size:13px;font-weight:600;"
        f"background:{header_bg};color:{text_c};border-bottom:2px solid {border_c};"
    )
    th_checkbox = f'<th style="{th_style}width:36px;"><input type="checkbox" style="width:14px;height:14px;cursor:pointer;"></th>'
    ths = th_checkbox + "".join(f'<th style="{th_style}">{c}</th>' for c in cols)
    thead = f'<thead><tr>{ths}</tr></thead>'

    # 数据行
    n_rows = random.randint(4, 10)
    tbody_rows = []
    all_metas = list(toolbar_metas)

    for row_i in range(n_rows):
        is_stripe = (row_i % 2 == 1)
        row_bg = stripe_bg if is_stripe else "transparent"
        td_style = (
            f"padding:9px 14px;font-size:13px;color:{text_c};"
            f"border-bottom:1px solid {border_c};background:{row_bg};"
        )
        td_cb = f'<td style="{td_style}width:36px;"><input type="checkbox" style="width:14px;height:14px;cursor:pointer;"></td>'

        # 数据单元格（除最后一列 Actions）
        data_cells = td_cb
        for col_idx, col in enumerate(cols[:-1]):
            sample_data = {
                "姓名": ["张三", "李四", "王五", "赵六"],
                "邮箱": ["user@example.com", "test@mail.com", "admin@site.org"],
                "角色": ["管理员", "普通用户", "编辑"],
                "状态": ["启用", "禁用", "待审核"],
                "商品名": ["iPhone 15", "MacBook Pro", "AirPods"],
                "价格": ["¥5999", "¥12999", "¥1299"],
                "库存": ["128", "32", "256"],
                "分类": ["手机", "电脑", "配件"],
                "Name": ["Alice", "Bob", "Carol", "Dave"],
                "Email": ["alice@corp.com", "bob@corp.com"],
                "Department": ["Engineering", "Marketing", "HR"],
                "Status": ["Active", "Inactive", "Pending"],
                "订单号": [f"ORD-{1000+row_i}", f"ORD-{2000+row_i}"],
                "客户": ["Alice", "Bob", "客户C"],
                "金额": ["¥299", "¥1,299", "¥59"],
                "时间": ["2024-01-15", "2024-02-20"],
                "ID": [str(row_i + 1)],
                "Title": ["Article A", "Post B", "Page C"],
                "Author": ["Admin", "Editor"],
                "Date": ["2024-01-10", "2024-03-05"],
            }.get(col, [f"data-{row_i}"])
            cell_val = random.choice(sample_data)
            data_cells += f'<td style="{td_style}">{cell_val}</td>'

        # 操作列（小按钮）
        action_btns = ""
        for act_label in random.choice([["编辑", "删除"], ["Edit", "Delete"], ["查看", "编辑"], ["View", "Edit", "Del"]]):
            act_color = "#dc3545" if act_label in ("删除", "Delete", "Del") else "#0d6efd"
            act_style = (
                f"padding:3px 10px;font-size:12px;border-radius:4px;cursor:pointer;"
                f"background:{act_color};color:#fff;border:none;margin-right:4px;"
            )
            action_btns += f'<button style="{act_style}">{act_label}</button>'
        data_cells += f'<td style="{td_style}">{action_btns}</td>'
        tbody_rows.append(f'<tr style="transition:background 0.15s;" onmouseover="this.style.background=\'{row_hover}\'" onmouseout="this.style.background=\'{row_bg}\'">{data_cells}</tr>')

    tbody = f'<tbody>{"".join(tbody_rows)}</tbody>'
    table_style = (
        f"width:100%;border-collapse:collapse;background:{bg};"
        f"border-radius:8px;overflow:hidden;"
        f"box-shadow:0 1px 4px rgba(0,0,0,0.08);"
    )
    table_html = f'<table style="{table_style}">{thead}{tbody}</table>'

    # 分页条
    pg_style = f"margin-top:16px;text-align:right;font-size:13px;color:{text_c};"
    pg_btn = f"padding:4px 10px;margin:0 2px;border:1px solid {border_c};border-radius:4px;background:transparent;color:{text_c};cursor:pointer;"
    pagination = (
        f'<div style="{pg_style}">'
        f'  <button style="{pg_btn}">‹</button>'
        + "".join(
            f'<button style="{pg_btn};{"background:#0d6efd;color:#fff;border-color:#0d6efd;" if i==1 else ""}">{i}</button>'
            for i in range(1, random.randint(3, 6))
        )
        + f'  <button style="{pg_btn}">›</button>'
        f'</div>'
    )

    container = (
        f'<div style="padding:24px;background:{bg};min-height:100vh;">'
        f'  {toolbar_html}'
        f'  {table_html}'
        f'  {pagination}'
        f'</div>'
    )
    return container, all_metas


# ─── P3: 导航栏布局 ─────────────────────────────────────
def _navbar_layout():
    """横向导航栏 + 内容区（模拟网站顶部导航）"""
    dark = random.random() < 0.35
    nav_bg    = random.choice(["#1a1a2e", "#0f172a", "#111827", "#1e293b"]) if dark else random.choice(["#ffffff", "#f8f9fa", "#1a1a2e"])
    nav_text  = "#e5e7eb" if (dark or nav_bg == "#1a1a2e") else "#374151"
    content_bg = "transparent"

    border_b  = "1px solid rgba(255,255,255,0.08)" if dark else "1px solid #e5e7eb"

    logo_text = random.choice(["MyApp", "Dashboard", "AdminPanel", "Brand", "SaaS"])

    # 导航链接
    nav_items = random.choice([
        ["首页", "产品", "文档", "关于"],
        ["Home", "Products", "Docs", "Pricing", "About"],
        ["概览", "用户", "订单", "设置"],
        ["Overview", "Analytics", "Reports", "Settings"],
    ])

    nav_link_style = (
        f"display:inline-block;padding:8px 14px;font-size:14px;"
        f"color:{nav_text};text-decoration:none;border-radius:4px;cursor:pointer;"
    )
    links_html = "".join(f'<a href="#" style="{nav_link_style}">{item}</a>' for item in nav_items)

    # 搜索框（50% 概率）
    search_html = ""
    search_meta = []
    if random.random() < 0.5:
        h, m = generate_input_html()
        search_html = f'<div style="margin:0 12px;">{h}</div>'
        search_meta.append(m)

    # 右侧按钮（登录/注册/头像）
    right_btns_html = ""
    right_metas = []
    for _ in range(random.randint(1, 2)):
        h, m = generate_button_html()
        right_btns_html += f'<div style="margin-left:8px;">{h}</div>'
        right_metas.append(m)

    nav_style = (
        f"display:flex;align-items:center;padding:0 24px;"
        f"height:56px;background:{nav_bg};"
        f"border-bottom:{border_b};"
        f"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
    )
    logo_style = (
        f"font-size:18px;font-weight:700;color:{nav_text};"
        f"margin-right:24px;text-decoration:none;"
    )
    navbar_html = (
        f'<nav style="{nav_style}">'
        f'  <a href="#" style="{logo_style}">{logo_text}</a>'
        f'  <div style="flex:1;display:flex;align-items:center;">{links_html}</div>'
        f'  {search_html}'
        f'  <div style="display:flex;align-items:center;">{right_btns_html}</div>'
        f'</nav>'
    )

    # 内容区（随机选一个已有布局的内容）
    inner_type = random.choice(["form", "mixed", "dashboard_content"])
    if inner_type == "form":
        inner_html, inner_metas = _form_layout()
    elif inner_type == "mixed":
        inner_html, inner_metas = _mixed_layout()
    else:
        n = random.randint(3, 6)
        inner_html, inner_metas = _random_elements(n, {"button": 25, "input": 20, "select": 15, "link": 15, "icon": 10, "checkbox": 8, "radio": 7})

    all_metas = search_meta + right_metas + list(inner_metas)
    container = (
        f'<div style="min-height:100vh;background:{content_bg};">'
        f'  {navbar_html}'
        f'  <div style="padding:24px;">{inner_html}</div>'
        f'</div>'
    )
    return container, all_metas


# ─── 新增: 排行榜/热榜布局 ──────────────────────────────────────
def _ranking_list_layout():
    """生成热榜/排行榜布局（带数字序号方块 + 文字标题链接）

    训练目的:
    - 让模型学会：数字序号方块 ≠ checkbox（纯背景元素，不标注）
    - 让模型学会：标题文字行 = link（标注为 link 类别）
    """
    dark = random.random() < 0.25
    bg        = random.choice(["#1e1e2e", "#0f172a"]) if dark else random.choice(["#fff", "#f8f9fa", "#fafafa"])
    text_c    = "#e2e8f0" if dark else "#212529"
    border_c  = "#374151" if dark else "#e5e7eb"
    sub_c     = "#94a3b8" if dark else "#6b7280"

    # 热榜标题
    board_titles = ["热搜榜", "热榜", "实时热点", "百度热搜", "微博热搜",
                    "知乎热榜", "今日热点", "推荐阅读", "Hot Topics", "Trending"]
    board_title = random.choice(board_titles)

    n_items = random.randint(8, 15)
    titles  = random.choices(RANKING_TITLES, k=n_items)

    # 序号颜色（前3名特殊颜色，其余灰色）
    rank_colors = [
        ("#ff2442", "#fff"),   # 1
        ("#ff6b35", "#fff"),   # 2
        ("#ffa500", "#fff"),   # 3
    ]
    default_rank_color = ("#e5e7eb" if not dark else "#374151", "#6b7280")

    rows_html = []
    metas     = []

    for i, title in enumerate(titles):
        rank = i + 1
        if rank <= 3:
            rb_bg, rb_c = rank_colors[rank - 1]
        else:
            rb_bg, rb_c = default_rank_color

        # 序号方块（纯视觉元素，不可交互，renderer 不会把它标注为任何类别）
        rank_style = (
            f"display:inline-flex;align-items:center;justify-content:center;"
            f"width:{random.choice([18,20,22])}px;height:{random.choice([18,20,22])}px;"
            f"background:{rb_bg};color:{rb_c};"
            f"font-size:11px;font-weight:600;"
            f"border-radius:{random.choice(['2px','3px','4px'])};"
            f"flex-shrink:0;margin-right:8px;"
        )
        rank_html = f'<span style="{rank_style}">{rank}</span>'

        # 标题链接（<a> 标签，会被 renderer 标注为 link）
        href = random.choice(["#", "javascript:void(0)"])
        link_style = (
            f"color:{text_c};font-size:{random.choice(['14px','15px','16px'])};"
            f"text-decoration:none;cursor:pointer;flex:1;"
            f"font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;"
            f"line-height:1.5;"
        )
        link_html = f'<a href="{href}" style="{link_style}">{title}</a>'
        metas.append({"type": "link", "style": "news_row", "text": title})

        # 热度标签（部分条目，纯展示用）
        tag_html = ""
        if random.random() < 0.35:
            tag_colors = [("#fef2f2", "#ef4444"), ("#fff7ed", "#f97316"),
                          ("#f0fdf4", "#22c55e"), ("#eff6ff", "#3b82f6")]
            tag_bg, tag_c = random.choice(tag_colors)
            tag_text = random.choice(["热", "新", "沸", "荐", "爆"])
            tag_style = (
                f"display:inline-block;padding:0 4px;font-size:10px;"
                f"background:{tag_bg};color:{tag_c};border-radius:2px;"
                f"margin-left:4px;flex-shrink:0;"
            )
            tag_html = f'<span style="{tag_style}">{tag_text}</span>'

        # 热度数字
        heat_html = ""
        if random.random() < 0.6:
            heat = random.randint(10, 999)
            heat_style = f"font-size:12px;color:{sub_c};margin-left:8px;flex-shrink:0;"
            heat_html = f'<span style="{heat_style}">{heat}万</span>'

        row_style = (
            f"display:flex;align-items:center;"
            f"padding:{random.choice(['8px 0','10px 0','6px 0'])};"
            f"border-bottom:1px solid {border_c};"
        )
        rows_html.append(
            f'<div style="{row_style}">{rank_html}{link_html}{tag_html}{heat_html}</div>'
        )

    header_style = (
        f"display:flex;align-items:center;justify-content:space-between;"
        f"margin-bottom:12px;padding-bottom:8px;"
        f"border-bottom:2px solid {border_c};"
    )
    title_style = f"font-size:16px;font-weight:600;color:{text_c};"
    card_style = (
        f"background:{bg};border-radius:8px;"
        f"padding:{random.choice(['16px','20px','24px'])};"
        f"max-width:{random.randint(360, 600)}px;"
        f"box-shadow:0 1px 4px rgba(0,0,0,0.08);"
    )

    # 可能并排两列
    if random.random() < 0.4:
        n2 = random.randint(6, 12)
        titles2 = random.choices(RANKING_TITLES, k=n2)
        rows2 = []
        for i2, t2 in enumerate(titles2):
            rank2 = i2 + 1
            if rank2 <= 3:
                rb_bg2, rb_c2 = rank_colors[rank2 - 1]
            else:
                rb_bg2, rb_c2 = default_rank_color
            rs2 = (
                f"display:inline-flex;align-items:center;justify-content:center;"
                f"width:20px;height:20px;background:{rb_bg2};color:{rb_c2};"
                f"font-size:11px;font-weight:600;border-radius:3px;"
                f"flex-shrink:0;margin-right:8px;"
            )
            ls2 = (
                f"color:{text_c};font-size:14px;text-decoration:none;"
                f"cursor:pointer;flex:1;"
                f"font-family:-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif;"
            )
            rows2.append(
                f'<div style="display:flex;align-items:center;padding:8px 0;border-bottom:1px solid {border_c};">'
                f'<span style="{rs2}">{rank2}</span>'
                f'<a href="#" style="{ls2}">{t2}</a></div>'
            )
            metas.append({"type": "link", "style": "news_row", "text": t2})

        col2_style = (
            f"background:{bg};border-radius:8px;"
            f"padding:16px;max-width:480px;"
            f"box-shadow:0 1px 4px rgba(0,0,0,0.08);margin-left:24px;"
        )
        col1 = f'<div style="{card_style}"><div style="{header_style}"><span style="{title_style}">{board_title}</span></div>{"".join(rows_html)}</div>'
        col2 = f'<div style="{col2_style}"><div style="{header_style}"><span style="{title_style}">{random.choice(board_titles)}</span></div>{"".join(rows2)}</div>'
        return f'<div style="display:flex;flex-wrap:wrap;gap:24px;padding:24px;">{col1}{col2}</div>', metas

    card_html = (
        f'<div style="{card_style}">'
        f'  <div style="{header_style}">'
        f'    <span style="{title_style}">{board_title}</span>'
        f'  </div>'
        f'  {"".join(rows_html)}'
        f'</div>'
    )
    return f'<div style="padding:24px;">{card_html}</div>', metas


# ─── 新增: 新闻资讯流布局 ─────────────────────────────────────
def _news_feed_layout():
    """生成新闻列表布局（纯文字链接行 + 分类/时间辅助信息）"""
    dark = random.random() < 0.2
    bg     = random.choice(["#0f172a", "#111827"]) if dark else random.choice(["#fff", "#f8f9fa"])
    text_c = "#e2e8f0" if dark else "#212529"
    sub_c  = "#94a3b8" if dark else "#9ca3af"
    border_c = "#374151" if dark else "#e5e7eb"

    categories = ["国内", "国际", "科技", "财经", "娱乐", "体育",
                  "Tech", "Finance", "Sports", "Entertainment"]

    n_items = random.randint(6, 14)
    parts   = []
    metas   = []

    # 分类标签行（可选）
    if random.random() < 0.6:
        cats = random.sample(categories, random.randint(3, 6))
        cat_html = "".join(
            f'<span style="display:inline-block;padding:4px 12px;margin:0 4px 8px 0;'
            f'border-radius:20px;font-size:13px;cursor:pointer;'
            f'background:{"#1e3a5f" if dark else "#eff6ff"};'
            f'color:{"#93c5fd" if dark else "#3b82f6"};">{c}</span>'
            for c in cats
        )
        parts.append(f'<div style="margin-bottom:16px;">{cat_html}</div>')

    for _ in range(n_items):
        title = random.choice(RANKING_TITLES)
        href  = "#"
        lh    = random.choice(["1.5", "1.6"])
        fs    = random.choice(["14px", "15px", "16px"])
        link_style = (
            f"display:block;color:{text_c};font-size:{fs};"
            f"text-decoration:none;cursor:pointer;line-height:{lh};"
            f"font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;"
            f"padding:10px 0;"
        )
        link_html = f'<a href="{href}" style="{link_style}">{title}</a>'
        metas.append({"type": "link", "style": "news_row", "text": title})

        # 副信息行（来源 + 时间）
        source = random.choice(["新华社", "人民日报", "澎湃", "36氪", "BBC", "Reuters"])
        time_str = random.choice(["1小时前", "2小时前", "刚刚", "30分钟前", "1天前"])
        sub_style = f"font-size:12px;color:{sub_c};padding-bottom:8px;"
        sub_html  = f'<div style="{sub_style}">{source} · {time_str}</div>'

        row_style = f"border-bottom:1px solid {border_c};"
        parts.append(f'<div style="{row_style}">{link_html}{sub_html}</div>')

    container_style = (
        f"background:{bg};border-radius:8px;"
        f"padding:{random.choice(['16px','20px','24px'])};"
        f"max-width:{random.randint(480, 800)}px;"
    )
    return f'<div style="padding:24px;"><div style="{container_style}">{"" .join(parts)}</div></div>', metas


# ─── 新增: 社交卡片布局（点赞/评论/分享按钮）─────────────────
def _social_card_layout():
    """生成社交内容卡片（含图标+文字的轻量操作按钮）

    训练目的: 让模型识别「点赞/评论/分享/关注/阅读全文」类轻量按钮
    """
    dark = random.random() < 0.2
    bg     = random.choice(["#0f172a", "#1e1e2e"]) if dark else random.choice(["#fff", "#f8f9fa"])
    text_c = "#e2e8f0" if dark else "#1f2937"
    sub_c  = "#94a3b8" if dark else "#6b7280"
    border_c = "#374151" if dark else "#e5e7eb"

    action_configs = [
        # (图标FA, 文字选项列表, 颜色)
        ("fa-solid fa-thumbs-up",   ["赞 {n}", "点赞 {n}", "Like {n}", "👍 {n}"], sub_c),
        ("fa-solid fa-comment",     ["评论 {n}", "回复 {n}", "Comment {n}"], sub_c),
        ("fa-solid fa-share-nodes", ["分享", "转发", "Share"], sub_c),
        ("fa-solid fa-bookmark",    ["收藏", "书签", "Save"], sub_c),
        ("fa-solid fa-ellipsis",    ["更多", "...", "More"], sub_c),
    ]

    def _icon_text_btn(icon_cls, texts, color):
        """生成图标+文字的轻量按钮"""
        n    = random.randint(0, 9999)
        text = random.choice(texts).format(n=n)
        fs   = random.choice(["12px", "13px", "14px"])
        pad  = random.choice(["4px 8px", "4px 10px", "6px 10px", "4px 12px"])
        bg_b = random.choice(["transparent", "transparent", "#f3f4f6", "rgba(0,0,0,0.04)"])
        style = (
            f"display:inline-flex;align-items:center;gap:4px;"
            f"padding:{pad};border-radius:6px;"
            f"background:{bg_b};border:none;cursor:pointer;"
            f"color:{color};font-size:{fs};"
            f"font-family:-apple-system,BlinkMacSystemFont,sans-serif;"
        )
        icon_style = f"font-size:{fs};color:{color};"
        return (
            f'<button style="{style}">'
            f'<i class="{icon_cls}" style="{icon_style}"></i>{text}</button>'
        ), {"type": "button", "style": "icon_text"}

    n_cards = random.randint(2, 5)
    card_parts = []

    for _ in range(n_cards):
        # 卡片内容（摘要文字）
        snippets = [
            "这是一篇关于人工智能的文章，探讨了AI对未来工作的影响。",
            "2026年，Mac和Win的选择困境依然困扰着不少用户。",
            "研究表明，每天步行11000步可有效延长寿命。",
            "How does AI affect the future of programming jobs?",
            "New research shows walking 10,000 steps daily improves health.",
            "DeepSeek v4发布，百万token上下文引发热议。",
        ]
        content = random.choice(snippets)
        metas_card = []

        # 操作按钮行
        n_actions = random.randint(2, 4)
        selected_actions = random.sample(action_configs, n_actions)
        btn_parts = []
        for icon_cls, texts, color in selected_actions:
            bhtml, bmeta = _icon_text_btn(icon_cls, texts, color)
            btn_parts.append(bhtml)
            metas_card.append(bmeta)

        # 「阅读全文」链接（50%概率）
        read_more_html = ""
        if random.random() < 0.5:
            rm_style = (
                f"color:{random.choice(['#1677ff','#0d6efd','#3b82f6'])};"
                f"font-size:13px;text-decoration:none;cursor:pointer;"
            )
            read_more_html = f' <a href="#" style="{rm_style}">阅读全文</a>'
            metas_card.append({"type": "link", "style": "action_text"})

        content_style = f"font-size:14px;color:{text_c};line-height:1.6;margin-bottom:8px;"
        actions_style = f"display:flex;align-items:center;gap:4px;flex-wrap:wrap;"
        card_style = (
            f"background:{bg};border-radius:8px;"
            f"padding:{random.choice(['16px','20px'])};"
            f"border:1px solid {border_c};"
            f"margin-bottom:12px;"
        )
        card_parts.append(
            f'<div style="{card_style}">'
            f'  <div style="{content_style}">{content}{read_more_html}</div>'
            f'  <div style="{actions_style}">{" ".join(btn_parts)}</div>'
            f'</div>'
        )

    return f'<div style="padding:24px;max-width:680px;">{"" .join(card_parts)}</div>', metas_card
