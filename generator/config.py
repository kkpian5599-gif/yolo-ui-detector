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
    "请输入", "请输入用户名", "请输入密码", "请输入邮箱", "搜索...",
    "Please enter", "Username", "Password", "Email", "Search...",
]

LINK_TEXTS = [
    "了解更多", "查看详情", "忘记密码?", "立即注册", "帮助中心",
    "隐私政策", "服务条款", "联系我们", "关于我们",
    "Learn more", "Forgot password?", "Help", "Contact us",
]

# 快捷引用
DARK = STYLE_PROFILE["dark_theme"]

# 页面尺寸
PAGE_SIZES = [
    (1366, 768),   # 常见笔记本
    (1440, 900),   # MacBook
    (1920, 1080),  # 标准桌面
    (1280, 720),   # 小屏幕
]
