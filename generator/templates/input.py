"""输入框/表单控件HTML生成器"""
import random
from ..config import STYLE_PROFILE, INPUT_PLACEHOLDERS

INP = STYLE_PROFILE["inputs"]
SIZES = INP["sizes"]


# 渐变边框预设（用于 input / textarea wrapper 套壳技巧）
GRADIENT_BORDERS = [
    # (渐变CSS, 边框厚度px, 描述)
    ("linear-gradient(135deg,#667eea,#764ba2)", 2, "blue_purple"),
    ("linear-gradient(135deg,#f093fb,#f5576c)", 2, "pink_red"),
    ("linear-gradient(135deg,#4facfe,#00f2fe)", 2, "sky_blue"),
    ("linear-gradient(135deg,#43e97b,#38f9d7)", 2, "green_teal"),
    ("linear-gradient(135deg,#fa709a,#fee140)", 2, "pink_gold"),
    ("linear-gradient(90deg,#f7971e,#ffd200)", 2, "orange_gold"),
    ("linear-gradient(90deg,#11998e,#38ef7d)", 2, "emerald"),
    ("linear-gradient(135deg,#6a11cb,#2575fc)", 2, "violet_blue"),
    ("linear-gradient(135deg,#f83600,#f9d423)", 2, "red_gold"),
    ("linear-gradient(135deg,#0f3460,#533483,#e94560)", 2, "deep_rainbow"),
    ("linear-gradient(90deg,#ff6b6b,#feca57,#48dbfb,#ff9ff3)", 2, "rainbow"),
    ("linear-gradient(135deg,#a18cd1,#fbc2eb)", 2, "lavender_pink"),
    ("linear-gradient(135deg,#ffecd2,#fcb69f)", 2, "peach"),
    ("linear-gradient(135deg,#a1c4fd,#c2e9fb)", 2, "light_blue"),
    ("linear-gradient(135deg,#d4fc79,#96e6a1)", 2, "lime_green"),
    ("linear-gradient(135deg,#667eea,#764ba2)", 3, "blue_purple_thick"),
    ("linear-gradient(135deg,#4facfe,#00f2fe)", 3, "sky_blue_thick"),
    ("linear-gradient(90deg,#f7971e,#ffd200)", 1, "gold_thin"),
]

# 炫酷特效样式预设
SPECIAL_EFFECTS = [
    # (style_suffix, 描述, 需要dark_bg)
    # --- 霓虹发光 Neon Glow ---
    ("border:2px solid #00ff41;background:#0a0a0a;color:#00ff41;font-family:monospace;"
     "box-shadow:0 0 8px #00ff41,0 0 20px #00ff4166,inset 0 0 8px #00ff4122;", "neon_green", True),
    ("border:2px solid #ff2d78;background:#0d0d1a;color:#ff2d78;font-family:monospace;"
     "box-shadow:0 0 8px #ff2d78,0 0 20px #ff2d7866,inset 0 0 8px #ff2d7822;", "neon_pink", True),
    ("border:2px solid #00cfff;background:#000d1a;color:#00cfff;font-family:monospace;"
     "box-shadow:0 0 8px #00cfff,0 0 24px #00cfff55,inset 0 0 8px #00cfff22;", "neon_blue", True),
    ("border:2px solid #bf5fff;background:#0d001a;color:#bf5fff;font-family:monospace;"
     "box-shadow:0 0 8px #bf5fff,0 0 20px #bf5fff55;", "neon_purple", True),
    ("border:2px solid #ff9000;background:#0d0500;color:#ff9000;font-family:monospace;"
     "box-shadow:0 0 10px #ff9000,0 0 24px #ff900044;", "neon_orange", True),
    # --- 新拟态 Neumorphism ---
    ("border:none;background:#e0e5ec;color:#333;"
     "box-shadow:6px 6px 14px #b8bec7,-6px -6px 14px #ffffff;", "neumorph_flat", False),
    ("border:none;background:#e0e5ec;color:#333;"
     "box-shadow:inset 4px 4px 10px #b8bec7,inset -4px -4px 10px #ffffff;", "neumorph_pressed", False),
    ("border:none;background:#1e2a3a;color:#cdd9e5;"
     "box-shadow:6px 6px 14px #131c27,-6px -6px 14px #29384d;", "neumorph_dark", True),
    # --- 玻璃拟态 Glassmorphism ---
    ("border:1px solid rgba(255,255,255,0.4);background:rgba(255,255,255,0.18);color:#1a1a2e;"
     "backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);"
     "box-shadow:0 4px 24px rgba(0,0,0,0.12);", "glass_light", False),
    ("border:1px solid rgba(255,255,255,0.15);background:rgba(255,255,255,0.08);color:#e8eaf6;"
     "backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);"
     "box-shadow:0 4px 24px rgba(0,0,0,0.3);", "glass_dark", True),
    ("border:1px solid rgba(100,180,255,0.35);background:rgba(100,180,255,0.12);color:#1a2a4a;"
     "backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);"
     "box-shadow:0 4px 20px rgba(100,180,255,0.2);", "glass_blue", False),
    # --- 赛博朋克 Cyberpunk ---
    ("border:2px solid #f0f;background:#0a0010;color:#f0f;"
     "box-shadow:2px 2px 0 #0ff,-2px -2px 0 #f0f;"
     "font-family:monospace;letter-spacing:1px;", "cyber_glitch", True),
    ("border-top:2px solid #ffd700;border-bottom:2px solid #ff4500;"
     "border-left:none;border-right:none;background:#0a0a0a;color:#ffd700;"
     "font-family:monospace;letter-spacing:2px;", "cyber_gold", True),
    # --- 双边框 Double Border ---
    ("border:2px solid #1890ff;outline:4px solid #1890ff33;outline-offset:2px;"
     "background:#fff;color:#212529;", "double_border_blue", False),
    ("border:2px solid #52c41a;outline:4px solid #52c41a33;outline-offset:2px;"
     "background:#fff;color:#212529;", "double_border_green", False),
    ("border:3px solid #212529;outline:3px solid #212529;outline-offset:3px;"
     "background:#fff;color:#212529;", "double_border_dark", False),
    # --- 复古终端 Retro Terminal ---
    ("border:1px solid #33ff33;background:#001100;color:#33ff33;"
     "font-family:'Courier New',monospace;letter-spacing:1px;"
     "box-shadow:inset 0 0 20px #00330066;", "retro_terminal", True),
    ("border:1px solid #ff8c00;background:#1a0d00;color:#ff8c00;"
     "font-family:'Courier New',monospace;"
     "box-shadow:inset 0 0 12px #ff8c0033;", "retro_amber", True),
    # --- 彩色实线粗边框 Bold Solid ---
    ("border:3px solid #ff4757;background:#fff;color:#212529;", "bold_red", False),
    ("border:3px solid #2ed573;background:#fff;color:#212529;", "bold_green", False),
    ("border:3px solid #1e90ff;background:#fff;color:#212529;", "bold_blue", False),
    ("border:3px solid #ffa502;background:#fff;color:#212529;", "bold_orange", False),
]

# ── 图标系统：Font Awesome 6 / Bootstrap Icons ─────────────────────
# 格式: {"fa": "<i class...>", "bi": "<i class...>"}
_ICONS = {
    "search":   {"fa": "fa-solid fa-magnifying-glass", "bi": "bi bi-search"},
    "mic":      {"fa": "fa-solid fa-microphone",       "bi": "bi bi-mic"},
    "camera":   {"fa": "fa-solid fa-camera",           "bi": "bi bi-camera"},
    "filter":   {"fa": "fa-solid fa-filter",           "bi": "bi bi-funnel"},
    "close":    {"fa": "fa-solid fa-xmark",            "bi": "bi bi-x-lg"},
    "email":    {"fa": "fa-solid fa-envelope",         "bi": "bi bi-envelope"},
    "lock":     {"fa": "fa-solid fa-lock",             "bi": "bi bi-lock"},
    "user":     {"fa": "fa-solid fa-user",             "bi": "bi bi-person"},
    "phone":    {"fa": "fa-solid fa-phone",            "bi": "bi bi-telephone"},
    "key":      {"fa": "fa-solid fa-key",              "bi": "bi bi-key"},
    "eye":      {"fa": "fa-solid fa-eye",              "bi": "bi bi-eye"},
    "globe":    {"fa": "fa-solid fa-globe",            "bi": "bi bi-globe"},
    "star":     {"fa": "fa-solid fa-star",             "bi": "bi bi-star"},
    "home":     {"fa": "fa-solid fa-house",            "bi": "bi bi-house"},
    "map":      {"fa": "fa-solid fa-location-dot",     "bi": "bi bi-geo-alt"},
    "calendar": {"fa": "fa-solid fa-calendar",         "bi": "bi bi-calendar"},
    "comment":  {"fa": "fa-solid fa-comment",          "bi": "bi bi-chat"},
    "pencil":   {"fa": "fa-solid fa-pencil",           "bi": "bi bi-pencil"},
    "code":     {"fa": "fa-solid fa-code",             "bi": "bi bi-code-slash"},
    "link":     {"fa": "fa-solid fa-link",             "bi": "bi bi-link-45deg"},
    "image":    {"fa": "fa-solid fa-image",            "bi": "bi bi-image"},
    "file":     {"fa": "fa-solid fa-file",             "bi": "bi bi-file-text"},
}

def _icon_html(name, lib=None, color="#999", size="14px", extra_style=""):
    """生成一个图标 <i> 标签，lib 为 'fa'/'bi'，None 则随机"""
    if lib is None:
        lib = random.choice(["fa", "bi"])
    cls = _ICONS.get(name, _ICONS["search"])[lib]
    return (
        f'<i class="{cls}" style="color:{color};font-size:{size};'
        f'pointer-events:none;{extra_style}"></i>'
    )


def _icon_input_wrapper(inner_html, left_icon=None, right_icon=None,
                         lib=None, icon_color="#aaa", bg="transparent", radius="6px"):
    """给 input/textarea 加左右图标的 position:relative wrapper"""
    left_html = ""
    right_html = ""
    if left_icon:
        i = _icon_html(left_icon, lib, color=icon_color,
                        extra_style="position:absolute;left:12px;top:50%;transform:translateY(-50%);")
        left_html = i
    if right_icon:
        icons = right_icon if isinstance(right_icon, list) else [right_icon]
        offset = 10
        for ic in reversed(icons):
            extra = (f"position:absolute;right:{offset}px;top:50%;"
                     f"transform:translateY(-50%);cursor:pointer;")
            right_html += _icon_html(ic, lib, color=icon_color, extra_style=extra)
            offset += 22
    wrapper_style = (
        f"position:relative;display:inline-block;"
        f"background:{bg};border-radius:{radius};"
    )
    return f'<span style="{wrapper_style}">{left_html}{inner_html}{right_html}</span>'



def _gradient_border_wrapper(inner_html, gradient, thickness, radius_outer, radius_inner, display="inline-block"):
    """用渐变背景+padding套壳实现渐变边框效果"""
    wrapper_style = (
        f"display:{display};"
        f"background:{gradient};"
        f"padding:{thickness}px;"
        f"border-radius:{radius_outer};"
    )
    inner_wrapper_style = (
        f"display:block;"
        f"border-radius:{radius_inner};"
        f"overflow:hidden;"
    )
    return f'<span style="{wrapper_style}"><span style="{inner_wrapper_style}">{inner_html}</span></span>'


def generate_input_html():
    """生成 input，含渐变边框/霓虹/玻璃/新拟态/赛博朋克等特效变体"""
    size = random.choice(list(SIZES.keys()))
    s = SIZES[size]
    input_type = random.choice(["text", "text", "text", "password", "email"])
    placeholder = random.choice(INPUT_PLACEHOLDERS)
    disabled = random.random() < 0.05

    w = random.randint(120, 350)
    font_family = random.choice([
        "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif",
        "Arial,sans-serif",
        "'Microsoft YaHei',微软雅黑,sans-serif",
        "Helvetica,Arial,sans-serif",
    ])

    # 特效概率分配（disabled时退回普通）
    effect_roll = random.random() if not disabled else 1.0
    effect_name = "normal"
    inp_html = ""

    if effect_roll < 0.18:  # 渐变边框
        gradient, thickness, _gname = random.choice(GRADIENT_BORDERS)
        radius_num = random.choice([4, 6, 8, 10, 20])
        ro, ri = f"{radius_num}px", f"{max(1,radius_num-thickness)}px"
        inner_style = (
            f"width:{w}px;height:{s['h']};padding:{s['pad']};font-size:{s['fs']};"
            f"border:none;border-radius:{ri};background:#fff;color:#212529;"
            f"font-family:{font_family};outline:none;box-sizing:border-box;display:block;"
        )
        inner = f'<input placeholder="{placeholder}" type="{input_type}" style="{inner_style}">'
        inp_html = _gradient_border_wrapper(inner, gradient, thickness, ro, ri)
        effect_name = f"gradient_{_gname}"

    elif effect_roll < 0.35:  # 炫酷特效
        fx_style, fx_name, _dark = random.choice(SPECIAL_EFFECTS)
        radius = random.choice(["4px", "6px", "8px", "0px", "20px"])
        style = (
            f"width:{w}px;height:{s['h']};padding:{s['pad']};font-size:{s['fs']};"
            f"border-radius:{radius};outline:none;box-sizing:border-box;"
            f"{fx_style}"
        )
        inp_html = f'<input placeholder="{placeholder}" type="{input_type}" style="{style}">'
        effect_name = fx_name

    else:  # 普通样式
        style = (
            f"width:{w}px;height:{s['h']};padding:{s['pad']};font-size:{s['fs']};"
            f"border-radius:{s['r']};border:1px solid #dee2e6;"
            f"background:#fff;color:#212529;font-family:{font_family};"
            f"outline:none;box-sizing:border-box;"
        )
        if disabled:
            style += "background:#e9ecef;color:#6c757d;cursor:not-allowed;"
        extra = f' placeholder="{placeholder}"'
        if disabled:
            extra += " disabled"
        extra += f' type="{input_type}"'
        inp_html = f'<input{extra} style="{style}">'

    # ── 图标装饰（50%概率，仅普通/特效样式，渐变边框已有特效不重叠）──
    if effect_name in ("normal",) and not disabled and random.random() < 0.50:
        # 根据 input_type / placeholder 推断图标
        if input_type == "password":
            left_icon = random.choice(["lock", "key"])
        elif input_type == "email":
            left_icon = "email"
        elif "搜索" in placeholder or "search" in placeholder.lower():
            left_icon = "search"
        elif "手机" in placeholder or "phone" in placeholder.lower():
            left_icon = "phone"
        else:
            left_icon = random.choice(["user", "globe", "home", "star", None, None])

        right_icon = None
        if "搜索" in placeholder or "search" in placeholder.lower():
            right_icon = random.choice(["mic", "filter", None])
        elif input_type == "password":
            right_icon = random.choice(["eye", None])

        if left_icon:
            # 内层 input 加 padding-left 给图标留空间
            inp_html = inp_html.replace("outline:none", "padding-left:36px;outline:none")
            inp_html = _icon_input_wrapper(inp_html, left_icon=left_icon,
                                           right_icon=right_icon, radius=s["r"], bg="#fff")

    # label（70%概率有）
    label_html = ""
    if random.random() < 0.7:
        label_style = f"display:block;font-size:{s['fs']};margin-bottom:4px;color:#333;font-family:{font_family};"
        label_text = random.choice(["用户名", "密码", "邮箱", "手机号", "地址", "搜索", "Username", "Email", "Name"])
        label_html = f'<label style="{label_style}">{label_text}</label>'

    return f'{label_html}{inp_html}', {"type": f"input_{input_type}", "size": size, "disabled": disabled, "effect": effect_name}



def generate_checkbox_html():
    """生成复选框 + label"""
    checked = random.random() < 0.3
    disabled = random.random() < 0.05
    label_text = random.choice(["记住密码", "同意协议", "订阅通知", "Remember me", "I agree"])

    chk = f'<input type="checkbox"{" checked" if checked else ""}{" disabled" if disabled else ""} style="width:16px;height:16px;margin:0 8px 0 0;vertical-align:middle;accent-color:#0d6efd;">'
    lbl = f'<span style="font-size:14px;color:#212529;font-family:-apple-system,BlinkMacSystemFont,sans-serif;vertical-align:middle;">{label_text}</span>'
    html = f'<label style="display:inline-flex;align-items:center;cursor:{"not-allowed" if disabled else "pointer"};">{chk}{lbl}</label>'
    return html, {"type": "checkbox", "checked": checked, "disabled": disabled}


def generate_radio_html():
    """生成单选框组（2-3个选项）"""
    group_name = f"radio_{random.randint(1000,9999)}"
    options = random.sample(["选项A", "选项B", "选项C", "男", "女", "Yes", "No", "Option 1", "Option 2", "Option 3"],
                            random.randint(2, 3))
    html_parts = []
    for i, opt in enumerate(options):
        checked = " checked" if i == 0 else ""
        radio = f'<input type="radio" name="{group_name}"{checked} style="width:16px;height:16px;margin:0 6px 0 0;vertical-align:middle;accent-color:#0d6efd;">'
        span = f'<span style="font-size:14px;color:#212529;margin-right:16px;font-family:-apple-system,BlinkMacSystemFont,sans-serif;vertical-align:middle;">{opt}</span>'
        html_parts.append(f'<label style="display:inline-flex;align-items:center;cursor:pointer;">{radio}{span}</label>')
    html = "".join(html_parts)
    return html, {"type": "radio", "count": len(options)}


def generate_select_html():
    """生成下拉选择框"""
    options = random.sample(["请选择", "选项1", "选项2", "选项3", "北京", "上海", "广州", "深圳",
                             "Choose...", "Option A", "Option B", "Option C"],
                            random.randint(3, 5))
    disabled = random.random() < 0.05

    style = (
        f"width:{random.randint(150,300)}px;"
        f"height:38px;"
        f"padding:6px 36px 6px 12px;"
        f"font-size:14px;"
        f"border-radius:6px;"
        f"border:1px solid #dee2e6;"
        f"background:#fff;"
        f"color:#212529;"
        f"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
        f"appearance:none;"
        f"background-image:url('data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 16 16\"><path fill=\"none\" stroke=\"%23333\" stroke-width=\"2\" d=\"M2 5l6 6 6-6\"/></svg>');"
        f"background-repeat:no-repeat;"
        f"background-position:right 12px center;"
        f"background-size:12px;"
        f"cursor:{'not-allowed' if disabled else 'pointer'};"
    )
    option_html = "".join(f'<option>{"selected " if i == 0 else ""}{o}</option>' for i, o in enumerate(options))
    html = f'<select{" disabled" if disabled else ""} style="{style}">{option_html}</select>'
    return html, {"type": "select", "options": len(options), "disabled": disabled}


def generate_textarea_html():
    """生成多行文本框 — 高度多样化版本，覆盖真实世界各种UI样式"""
    style_variant = random.choice([
        "standard", "standard", "standard",      # 普通表单风格（最常见）
        "search_box",                              # 搜索框风格（百度/Google类）
        "chat_input",                              # 聊天输入框
        "dark_theme",                              # 暗色主题
        "minimal_border",                          # 极简细边框
        "rounded_heavy",                           # 超圆角
        "flat_no_border",                          # 无边框底线
        "material_outlined",                       # Material Design outlined
        "focus_highlight",                         # 蓝色高亮焦点框
        "error_state",                             # 红色错误状态
        "success_state",                           # 绿色成功状态
        "disabled_state",                          # 禁用状态
        "filled_background",                       # 填充背景
        "shadow_card",                             # 投影卡片式
        "compact_sm",                              # 紧凑小型
        "large_editor",                            # 大型编辑器
        "code_style",                              # 代码输入框风格
        "comment_box",                             # 评论框风格
        "with_content",                            # 带内容文字（非空）
        "with_content",
        "gradient_border",                         # 渐变边框
        "gradient_border",                         # 渐变边框（权重翻倍）
        "gradient_border_dark",                    # 渐变边框+暗色背景
        "gradient_border_rounded",                 # 渐变边框+大圆角
        "special_effect",                          # 霓虹/新拟态/玻璃/赛博朋克等
        "special_effect",                          # （权重翻倍）
    ])

    # 通用内容
    PLACEHOLDERS = [
        "请输入详细描述...", "请输入备注...", "请输入留言...", "请输入问题...",
        "请输入地址...", "请输入自我介绍...", "请输入内容...", "在这里输入...",
        "Enter description...", "Enter your message...", "Type something...",
        "Add a comment...", "Write here...", "Share your thoughts...",
        "Describe your issue...", "Additional notes...", "Remarks...",
        "搜索...", "Search...", "百度一下，你就知道",
    ]
    SAMPLE_CONTENTS = [
        "这是一段示例文本内容，用于测试textarea显示效果。",
        "Hello, this is some sample content for the textarea.",
        "用户填写的反馈内容...\n第二行文字",
        "def hello():\n    print('world')",
        "订单备注：请在工作时间配送\n谢谢",
        "I have a question about your product.\nCould you please help me?",
    ]

    placeholder = random.choice(PLACEHOLDERS)
    w = random.randint(180, 500)
    h = random.randint(55, 160)
    font_size = random.choice(["12px", "13px", "14px", "15px", "16px"])
    font_family = random.choice([
        "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif",
        "Arial,sans-serif",
        "'Microsoft YaHei',微软雅黑,sans-serif",
        "Helvetica,Arial,sans-serif",
        "'PingFang SC','Hiragino Sans GB',sans-serif",
        "monospace",
    ])
    inner_text = ""

    if style_variant == "standard":
        border_color = random.choice(["#dee2e6", "#ced4da", "#d0d7de", "#e0e0e0", "#ccc", "#dcdfe6"])
        radius = random.choice(["4px", "6px", "8px", "4px"])
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:{random.choice(['6px 12px','8px 12px','6px 10px','8px 16px'])};"
            f"font-size:{font_size};border-radius:{radius};"
            f"border:1px solid {border_color};"
            f"background:#fff;color:#212529;"
            f"font-family:{font_family};"
            f"resize:{random.choice(['vertical','both','none','vertical'])};"
            f"outline:none;box-sizing:border-box;"
        )

    elif style_variant == "search_box":
        # 模拟百度/Google搜索框的圆角大输入框
        radius = random.choice(["22px", "24px", "20px", "18px", "16px"])
        border_color = random.choice(["#4e6ef2", "#c4c7ce", "#dfe1e5", "#1890ff"])
        shadow = random.choice(["0 2px 10px rgba(0,0,0,.1)", "0 1px 6px rgba(32,33,36,.28)", "none"])
        h_adj = random.randint(40, 72)
        style = (
            f"width:{random.randint(300,600)}px;height:{h_adj}px;"
            f"padding:8px 20px;"
            f"font-size:{random.choice(['14px','15px','16px'])};"
            f"border-radius:{radius};"
            f"border:1px solid {border_color};"
            f"background:#fff;color:#333;"
            f"font-family:{font_family};"
            f"resize:none;outline:none;box-sizing:border-box;"
            f"box-shadow:{shadow};"
        )

    elif style_variant == "chat_input":
        h_adj = random.randint(44, 80)
        style = (
            f"width:{random.randint(250,500)}px;height:{h_adj}px;"
            f"padding:10px 16px;"
            f"font-size:14px;border-radius:20px;"
            f"border:1px solid #e8e8e8;"
            f"background:#f5f5f5;color:#333;"
            f"font-family:{font_family};"
            f"resize:none;outline:none;box-sizing:border-box;"
        )

    elif style_variant == "dark_theme":
        bg = random.choice(["#1e1e1e", "#2d2d2d", "#252526", "#1a1a2e", "#0d1117", "#161b22"])
        border_c = random.choice(["#3c3c3c", "#444", "#30363d", "#555"])
        text_c = random.choice(["#d4d4d4", "#cdd9e5", "#e6edf3", "#abb2bf"])
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:8px 12px;font-size:{font_size};"
            f"border-radius:{random.choice(['6px','4px','8px'])};"
            f"border:1px solid {border_c};"
            f"background:{bg};color:{text_c};"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
        )

    elif style_variant == "minimal_border":
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:6px 8px;font-size:{font_size};"
            f"border-radius:2px;"
            f"border:1px solid #e8e8e8;"
            f"background:#fafafa;color:#333;"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
        )

    elif style_variant == "rounded_heavy":
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:10px 16px;font-size:{font_size};"
            f"border-radius:{random.choice(['12px','16px','20px'])};"
            f"border:2px solid {random.choice(['#e0e0e0','#d0d7de','#ced4da'])};"
            f"background:#fff;color:#212529;"
            f"font-family:{font_family};"
            f"resize:none;outline:none;box-sizing:border-box;"
        )

    elif style_variant == "flat_no_border":
        underline_color = random.choice(["#1890ff", "#4e6ef2", "#dcdfe6", "#ccc"])
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:6px 2px;font-size:{font_size};"
            f"border:none;border-bottom:2px solid {underline_color};"
            f"background:transparent;color:#212529;"
            f"font-family:{font_family};"
            f"resize:none;outline:none;box-sizing:border-box;"
        )

    elif style_variant == "material_outlined":
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:12px 14px;font-size:{font_size};"
            f"border-radius:4px;"
            f"border:2px solid {random.choice(['#1976d2','#9e9e9e','#3f51b5','#2196f3'])};"
            f"background:#fff;color:#212529;"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
        )

    elif style_variant == "focus_highlight":
        blue = random.choice(["#1890ff", "#4e6ef2", "#0d6efd", "#1677ff"])
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:8px 12px;font-size:{font_size};"
            f"border-radius:6px;"
            f"border:2px solid {blue};"
            f"background:#fff;color:#212529;"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
            f"box-shadow:0 0 0 3px {blue}33;"
        )

    elif style_variant == "error_state":
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:6px 12px;font-size:{font_size};"
            f"border-radius:6px;"
            f"border:1px solid #ff4d4f;"
            f"background:#fff2f0;color:#212529;"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
            f"box-shadow:0 0 0 2px #ff4d4f33;"
        )

    elif style_variant == "success_state":
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:6px 12px;font-size:{font_size};"
            f"border-radius:6px;"
            f"border:1px solid #52c41a;"
            f"background:#f6ffed;color:#212529;"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
        )

    elif style_variant == "disabled_state":
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:6px 12px;font-size:{font_size};"
            f"border-radius:6px;"
            f"border:1px solid #d9d9d9;"
            f"background:#f5f5f5;color:#00000040;"
            f"font-family:{font_family};"
            f"resize:none;outline:none;box-sizing:border-box;cursor:not-allowed;"
        )

    elif style_variant == "filled_background":
        bg = random.choice(["#f0f2f5", "#f5f5f5", "#f2f4f7", "#eef0f3", "#fafafa"])
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:8px 12px;font-size:{font_size};"
            f"border-radius:{random.choice(['6px','8px','10px'])};"
            f"border:1px solid transparent;"
            f"background:{bg};color:#333;"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
        )

    elif style_variant == "shadow_card":
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:10px 14px;font-size:{font_size};"
            f"border-radius:8px;"
            f"border:1px solid #f0f0f0;"
            f"background:#fff;color:#212529;"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
            f"box-shadow:0 2px 8px rgba(0,0,0,0.1);"
        )

    elif style_variant == "compact_sm":
        style = (
            f"width:{random.randint(120,220)}px;height:{random.randint(36,60)}px;"
            f"padding:4px 8px;font-size:12px;"
            f"border-radius:4px;"
            f"border:1px solid #dcdfe6;"
            f"background:#fff;color:#606266;"
            f"font-family:{font_family};"
            f"resize:none;outline:none;box-sizing:border-box;"
        )

    elif style_variant == "large_editor":
        style = (
            f"width:{random.randint(400,700)}px;height:{random.randint(150,280)}px;"
            f"padding:12px 16px;font-size:{random.choice(['14px','15px'])};"
            f"border-radius:6px;"
            f"border:1px solid #dee2e6;"
            f"background:#fff;color:#212529;"
            f"font-family:{font_family};"
            f"resize:both;outline:none;box-sizing:border-box;"
            f"line-height:1.6;"
        )

    elif style_variant == "code_style":
        style = (
            f"width:{w}px;height:{random.randint(80,160)}px;"
            f"padding:8px 12px;font-size:13px;"
            f"border-radius:6px;"
            f"border:1px solid #30363d;"
            f"background:#0d1117;color:#c9d1d9;"
            f"font-family:'Courier New',Consolas,monospace;"
            f"resize:vertical;outline:none;box-sizing:border-box;tab-size:4;"
        )
        placeholder = random.choice(["// Enter code here...", "# your code", "paste code..."])

    elif style_variant == "comment_box":
        style = (
            f"width:{random.randint(280,480)}px;height:{random.randint(70,120)}px;"
            f"padding:10px 14px;font-size:{font_size};"
            f"border-radius:8px;"
            f"border:1px solid #e4e6ea;"
            f"background:#f0f2f5;color:#333;"
            f"font-family:{font_family};"
            f"resize:none;outline:none;box-sizing:border-box;"
        )
        placeholder = random.choice(["Write a comment...", "Add a comment...", "说点什么..."])

    elif style_variant == "with_content":
        # 带有真实内容的 textarea（不是空的）
        inner_text = random.choice(SAMPLE_CONTENTS)
        border_color = random.choice(["#dee2e6", "#ced4da", "#dcdfe6"])
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:6px 12px;font-size:{font_size};"
            f"border-radius:6px;"
            f"border:1px solid {border_color};"
            f"background:#fff;color:#212529;"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
        )

    else:
        # fallback
        style = (
            f"width:{w}px;height:{h}px;"
            f"padding:6px 12px;font-size:{font_size};"
            f"border-radius:6px;border:1px solid #dee2e6;"
            f"background:#fff;color:#212529;"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;"
        )

    # label（50%概率有）
    label_html = ""
    if random.random() < 0.5:
        label_texts = [
            "备注", "描述", "内容", "留言", "问题", "地址", "简介", "评论",
            "Remarks", "Description", "Message", "Comment", "Notes", "Details",
        ]
        lbl_style = f"display:block;font-size:{font_size};margin-bottom:4px;color:#333;font-family:{font_family};"
        label_html = f'<label style="{lbl_style}">{random.choice(label_texts)}</label>'

    if style_variant in ("gradient_border", "gradient_border_dark", "gradient_border_rounded"):
        gradient, thickness, _gname = random.choice(GRADIENT_BORDERS)
        if style_variant == "gradient_border_rounded":
            radius_num = random.choice([16, 20, 24, 28])
        elif style_variant == "gradient_border_dark":
            radius_num = random.choice([4, 6, 8])
        else:
            radius_num = random.choice([4, 6, 8, 10])
        radius_outer = f"{radius_num}px"
        radius_inner = f"{max(1, radius_num - thickness)}px"
        if style_variant == "gradient_border_dark":
            bg_inner = random.choice(["#1e1e1e", "#2d2d2d", "#1a1a2e", "#0d1117"])
            text_c = random.choice(["#d4d4d4", "#e6edf3", "#abb2bf"])
        else:
            bg_inner = "#fff"
            text_c = "#212529"
        inner_style = (
            f"width:{w}px;height:{h}px;"
            f"padding:8px 12px;font-size:{font_size};"
            f"border:none;border-radius:{radius_inner};"
            f"background:{bg_inner};color:{text_c};"
            f"font-family:{font_family};"
            f"resize:vertical;outline:none;box-sizing:border-box;display:block;"
        )
        ta_inner = f'<textarea placeholder="{placeholder}" style="{inner_style}"></textarea>'
        wrapped = _gradient_border_wrapper(ta_inner, gradient, thickness, radius_outer, radius_inner, display="inline-block")
        return f'{label_html}{wrapped}', {"type": "textarea", "variant": style_variant, "gradient": _gname}

    if style_variant == "special_effect":
        fx_style, fx_name, _dark = random.choice(SPECIAL_EFFECTS)
        radius = random.choice(["4px", "6px", "8px", "0px", "12px"])
        sp_style = (
            f"width:{w}px;height:{h}px;"
            f"padding:8px 12px;font-size:{font_size};"
            f"border-radius:{radius};outline:none;box-sizing:border-box;"
            f"resize:vertical;"
            f"{fx_style}"
        )
        ta_html = f'<textarea placeholder="{placeholder}" style="{sp_style}"></textarea>'
        return f'{label_html}{ta_html}', {"type": "textarea", "variant": "special_effect", "effect": fx_name}

    if inner_text:
        ta_html = f'<textarea placeholder="{placeholder}" style="{style}">{inner_text}</textarea>'
    else:
        ta_html = f'<textarea placeholder="{placeholder}" style="{style}"></textarea>'

    # ── 图标装饰 ──────────────────────────────────────────────────
    if style_variant == "search_box":
        # 搜索框：左侧搜索图标 + 右侧随机（麦克风/相机/无）
        right_ic = random.choice(["mic", "camera", "filter", None, None])
        # 搜索框加左内边距给图标空间
        ta_html = ta_html.replace("padding:8px 20px", "padding:8px 20px 8px 40px")
        radius_val = random.choice(["22px", "24px", "20px"])
        ta_html = _icon_input_wrapper(ta_html, left_icon="search",
                                      right_icon=right_ic, radius=radius_val, bg="#fff")
    elif style_variant == "chat_input":
        right_ic = random.choice(["mic", "image", "link", None])
        ta_html = _icon_input_wrapper(ta_html, left_icon=None,
                                      right_icon=right_ic, radius="20px", bg="#f5f5f5")
    elif style_variant in ("comment_box", "standard") and random.random() < 0.30:
        left_ic = random.choice(["comment", "pencil", "file", None])
        if left_ic:
            ta_html = ta_html.replace("padding:8px 12px", "padding:8px 12px 8px 36px") \
                             .replace("padding:6px 12px", "padding:6px 12px 6px 36px") \
                             .replace("padding:10px 14px", "padding:10px 14px 10px 36px")
            ta_html = _icon_input_wrapper(ta_html, left_icon=left_ic, radius="8px")

    return f'{label_html}{ta_html}', {"type": "textarea", "variant": style_variant}

