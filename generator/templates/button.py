"""按钮HTML生成器 — 基于style_profile.json"""
import random
from ..config import STYLE_PROFILE, BTN_TEXTS

BTN = STYLE_PROFILE["buttons"]
COLORS = BTN["solid_colors"]
SOLID = BTN["solid"]
SIZES = ["small", "default", "large"]

STYLES = ["solid", "outline", "plain", "dashed", "round", "text_only", "text_with_bg"]


def random_button_style(disabled=False):
    """返回随机的按钮内联CSS样式字符串"""
    color_name = random.choice(list(COLORS.keys()))
    color = COLORS[color_name]
    size = random.choice(SIZES)
    style_type = random.choice(STYLES)

    pad = SOLID["padding"][size]
    fs = SOLID["font_size"][size]
    h = SOLID["height"][size]
    r = SOLID["radius"][size]

    base = f"display:inline-block;padding:{pad};font-size:{fs};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1;text-align:center;white-space:nowrap;cursor:{'not-allowed' if disabled else 'pointer'};user-select:none;"

    if style_type == "solid":
        if disabled:
            c = _lighten(color)
            base += f"background:{c};color:#fff;border:1px solid {c};border-radius:{r};opacity:1;"
        else:
            base += f"background:{color};color:#fff;border:1px solid {color};border-radius:{r};"

    elif style_type == "outline":
        if disabled:
            base += f"background:#fff;color:#a8abb2;border:1px solid #e4e7ed;border-radius:{r};"
        else:
            base += f"background:#fff;color:#606266;border:1px solid #dcdfe6;border-radius:{r};"

    elif style_type == "plain":
        tint = _tint(color)
        if disabled:
            base += f"background:{tint};color:#a0cfff;border:1px solid #d9ecff;border-radius:{r};"
        else:
            base += f"background:{tint};color:{color};border:1px solid {_lighter(color)};border-radius:{r};"

    elif style_type == "dashed":
        base += f"background:#fff;color:#606266;border:1px dashed #dcdfe6;border-radius:{r};"

    elif style_type == "round":
        if disabled:
            base += f"background:{_lighten(color)};color:#fff;border:1px solid {_lighten(color)};border-radius:20px;"
        else:
            base += f"background:{color};color:#fff;border:1px solid {color};border-radius:20px;"

    elif style_type == "text_only":
        if disabled:
            base += f"background:transparent;color:{_lighten(color)};border:none;border-radius:4px;"
        else:
            base += f"background:transparent;color:{color};border:none;border-radius:4px;"

    elif style_type == "text_with_bg":
        if disabled:
            base += f"background:#f5f7fa;color:#a0cfff;border:none;border-radius:4px;"
        else:
            base += f"background:#f5f7fa;color:{color};border:none;border-radius:4px;"

    return base, color_name, style_type, size


def generate_button_html(disabled=None):
    """生成一个完整的 <button> HTML 字符串"""
    if disabled is None:
        disabled = random.random() < 0.08  # 8% 概率 disabled
    style_css, color_name, style_type, size = random_button_style(disabled)
    text = random.choice(BTN_TEXTS)
    extra = " disabled" if disabled else ""
    return f'<button style="{style_css}"{extra}>{text}</button>', {
        "type": "button",
        "text": text,
        "disabled": disabled,
        "color": color_name,
        "style": style_type,
        "size": size,
    }


def _lighten(hex_color, factor=0.5):
    """将hex颜色变浅"""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def _tint(hex_color):
    """极浅色调（用于plain按钮背景）"""
    return _lighten(hex_color, 0.85)


def _lighter(hex_color):
    """浅色调（用于plain按钮边框）"""
    return _lighten(hex_color, 0.45)
