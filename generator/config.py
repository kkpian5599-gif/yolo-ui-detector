"""读取样式画像，定义YOLO类别映射"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROFILE_PATH = ROOT / "collected" / "style_profile.json"

try:
    STYLE_PROFILE = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
except FileNotFoundError:
    print(f"ERROR: style_profile.json not found at {PROFILE_PATH}", file=sys.stderr)
    print("Run Phase A first: use browser to collect CSS styles from real websites.", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON in {PROFILE_PATH}: {e}", file=sys.stderr)
    sys.exit(1)

# YOLO 类别定义
CLASSES = [
    "button",      # 0: 各种按钮
    "input",       # 1: 文本输入框
    "checkbox",    # 2: 复选框
    "radio",       # 3: 单选框
    "select",      # 4: 下拉选择框
    "textarea",    # 5: 多行文本框
    "link",        # 6: 超链接
    "icon",        # 7: 图标
    "modal",       # 8: 弹窗/遮罩
]

CLASS2ID = {name: i for i, name in enumerate(CLASSES)}
NUM_CLASSES = len(CLASSES)

# 常用中文文本（用于按钮、链接、placeholder）
BTN_TEXTS = [
    "提交", "确定", "取消", "搜索", "保存", "删除", "编辑", "新建",
    "导出", "导入", "刷新", "返回", "下一步", "上一步", "注册", "登录",
    "Submit", "OK", "Cancel", "Search", "Save", "Delete", "Edit", "New",
    "Export", "Import", "Refresh", "Back", "Next", "Prev", "Sign in", "Sign up",
]

INPUT_PLACEHOLDERS = [
    # 中文通用
    "请输入", "请输入用户名", "请输入密码", "请输入邮箱", "搜索...",
    "请输入手机号", "请输入验证码", "请输入昵称", "请输入真实姓名", "请输入地址",
    "请输入身份证号", "请输入公司名称", "请输入备注", "请输入关键字", "请输入网址",
    "请输入金额", "请输入数量", "请输入描述", "请输入标题", "请输入内容",
    "在此搜索...", "输入搜索词...", "输入城市/地区", "输入优惠码", "输入邮政编码",
    # 英文通用
    "Please enter", "Username", "Password", "Email", "Search...",
    "Enter your name", "Enter email address", "Enter phone number", "Enter verification code",
    "Enter your address", "Enter city", "Enter zip code", "Enter coupon code",
    "Enter amount", "Enter quantity", "Enter description", "Enter title",
    "Search for anything", "Find products...", "Search by keyword",
    "Type to search", "Filter results...", "Enter URL", "Enter company name",
    "Full name", "First name", "Last name", "Job title", "Department",
    "Card number", "MM/YY", "CVV", "Account number", "Confirm password",
    "New password", "Old password", "Re-enter password",
]

LINK_TEXTS = [
    "了解更多", "查看详情", "忘记密码?", "立即注册", "帮助中心",
    "隐私政策", "服务条款", "联系我们", "关于我们",
    "Learn more", "Forgot password?", "Help", "Contact us",
]

# 快捷引用
DARK = STYLE_PROFILE["dark_theme"]

# 训练/验证集分割比例
VAL_RATIO = 0.15  # 15% 作为 val 集

# 页面尺寸（含移动端，解决尺度泛化问题）
PAGE_SIZES = [
    # 桌面端（权重约 70%）
    (1366, 768),   # 常见笔记本
    (1440, 900),   # MacBook
    (1920, 1080),  # 标准桌面
    (1280, 720),   # 小屏幕
    (1536, 864),   # 常见 Windows 笔记本
    (1280, 800),   # 较小桌面
    # 移动端（权重约 30%）
    (390, 844),    # iPhone 14
    (375, 667),    # iPhone SE
    (414, 896),    # iPhone XR
    (360, 780),    # Android 通用
    (412, 915),    # Pixel 6
    # 平板端
    (768, 1024),   # iPad
    (820, 1180),   # iPad Air
]

# 尺寸权重：桌面:移动:平板 约 6:3:1
PAGE_SIZE_WEIGHTS = [
    10, 10, 8, 8, 8, 6,   # 桌面
    8, 6, 6, 6, 6,         # 移动
    4, 4,                  # 平板
]
