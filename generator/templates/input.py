"""输入框/表单控件HTML生成器"""
import random
from ..config import STYLE_PROFILE, INPUT_PLACEHOLDERS

INP = STYLE_PROFILE["inputs"]
SIZES = INP["sizes"]


def generate_input_html():
    """生成 <input type=text> 或 password 或 email"""
    size = random.choice(list(SIZES.keys()))
    s = SIZES[size]
    input_type = random.choice(["text", "text", "text", "password", "email"])
    placeholder = random.choice(INPUT_PLACEHOLDERS)
    disabled = random.random() < 0.05

    style = (
        f"width:{random.randint(120,350)}px;"
        f"height:{s['h']};"
        f"padding:{s['pad']};"
        f"font-size:{s['fs']};"
        f"border-radius:{s['r']};"
        f"border:1px solid #dee2e6;"
        f"background:#fff;"
        f"color:#212529;"
        f"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
        f"outline:none;box-sizing:border-box;"
    )
    if disabled:
        style += "background:#e9ecef;color:#6c757d;cursor:not-allowed;"

    extra = f' placeholder="{placeholder}"'
    if disabled:
        extra += " disabled"
    if input_type == "password":
        extra += ' type="password"'
    elif input_type == "email":
        extra += ' type="email"'
    else:
        extra += ' type="text"'

    # label（70%概率有）
    label_html = ""
    if random.random() < 0.7:
        label_style = f"display:block;font-size:{s['fs']};margin-bottom:4px;color:#333;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
        label_text = random.choice(["用户名", "密码", "邮箱", "手机号", "地址", "搜索", "Username", "Email", "Name"])
        label_html = f'<label style="{label_style}">{label_text}</label>'

    html = f'{label_html}<input{extra} style="{style}">'
    return html, {"type": f"input_{input_type}", "size": size, "disabled": disabled}


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
    """生成多行文本框"""
    placeholder = random.choice(["请输入详细描述...", "请输入备注...", "Enter description..."])
    style = (
        f"width:{random.randint(200,400)}px;"
        f"height:{random.randint(60,120)}px;"
        f"padding:6px 12px;"
        f"font-size:14px;"
        f"border-radius:6px;"
        f"border:1px solid #dee2e6;"
        f"background:#fff;"
        f"color:#212529;"
        f"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;"
        f"resize:vertical;"
        f"outline:none;box-sizing:border-box;"
    )
    html = f'<textarea placeholder="{placeholder}" style="{style}"></textarea>'
    return html, {"type": "textarea"}
