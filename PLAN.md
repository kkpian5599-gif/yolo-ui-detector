# YOLO11 合成数据生成器 — 详细设计

## 整体思路

分两阶段：

- 阶段 A：Hermes 抓取真实网页 → 分析样式规律 → 输出"样式画像"
- 阶段 B：合成数据生成器读取样式画像 → 模仿真实网页生成截图 → 自动标注

**不是简单随机，是"先学习真实网页长什么样，再模仿生成"。**

---

## 阶段 A：真实网页收集与分析

### A1. 抓取目标网站（10-15 个站，覆盖不同类型）

| 类型 | 示例网站 | 为什么选 |
|------|---------|---------|
| 后台管理 | 各种 admin panel demo | 表格、表单、按钮密集 |
| 电商 | 淘宝/京东商品页 | 复杂布局、价格标签、促销弹窗 |
| 文档站 | Vue/React 官方文档 | 代码块、侧边栏、搜索框 |
| 论坛 | V2EX、NGA | 列表、分页、用户卡片 |
| 工具站 | 在线计算器、转换器 | 表单密集、输入框多样 |
| SaaS | Notion、Figma 网页版 | 复杂 UI、tooltip、dropdown |
| 登录页 | GitHub/Google 登录 | 居中表单、社交登录按钮 |
| 落地页 | 各种产品首页 | Hero banner、CTA 按钮、卡片 |
| 暗色主题 | GitHub Dark、文档暗色模式 | 暗色背景下的元素样式 |
| 移动端 | 响应式站点的手机视图 | 小屏幕布局、汉堡菜单 |

### A2. 每个网页抓取什么

Hermes 用 browser 工具访问每个网页，提取：

```
1. 全页截图（1920x1080 或自适应）
2. DOM 快照 — 用 browser_console 提取所有交互元素：
   - 元素类型（button/a/input/select/textarea）
   - CSS computed style（颜色、字体、边框、阴影、圆角、尺寸）
   - 位置 bbox（getBoundingClientRect）
   - 层级关系（父子、兄弟）
3. 布局信息 — flex/grid 容器、列数、间距
4. 弹窗/遮罩 — 有无 modal、dropdown、tooltip、toast
5. 交互状态 — hover/focus/disabled 样式
```

### A3. 分析输出：样式画像

从 10-15 个网站中统计提炼，输出一份样式画像 JSON：

```json
{
  "button_styles": {
    "common_colors": ["#1890ff", "#1677ff", "#4096ff", "linear-gradient(...)"],
    "common_sizes": [
      {"padding": "4px 15px", "font_size": 14, "border_radius": 6},
      {"padding": "6px 16px", "font_size": 16, "border_radius": 8}
    ],
    "border_styles": ["solid 1px", "none", "outline"],
    "hover_patterns": ["brightness 0.9", "background darken"],
    "disabled_patterns": ["opacity 0.4", "grayscale"]
  },
  "input_styles": {
    "common_borders": ["1px solid #d9d9d9", "1px solid #e8e8e8"],
    "focus_borders": ["#4096ff", "box-shadow: 0 0 0 2px rgba(24,144,255,0.2)"],
    "placeholder_colors": ["#bfbfbf", "#999"],
    "common_heights": [32, 36, 40],
    "prefix_suffix": ["搜索图标", "¥符号", "单位后缀"]
  },
  "modal_styles": {
    "overlay": ["rgba(0,0,0,0.45)", "rgba(0,0,0,0.65)", "backdrop-filter: blur(4px)"],
    "common_buttons": ["确定+取消", "确认", "知道了"],
    "animation": ["fadeIn", "slideUp", "zoomIn"]
  },
  "layout_patterns": {
    "form": ["label左 input右", "label上 input下", "inline"],
    "table": ["striped rows", "bordered", "hover row highlight"],
    "card": ["shadow + border-radius", "border only", "flat"]
  },
  "dark_theme": {
    "bg": ["#141414", "#1f1f1f", "#0d1117"],
    "text": ["#e6e6e6", "#c9d1d9"],
    "border": ["#303030", "#424242"],
    "accent": ["#177ddc", "#58a6ff"]
  }
}
```

这份画像就是合成数据生成器的"配方"。

---

## 阶段 B：合成数据生成器

### B1. 整体架构

```
generator/
├── main.py                  — 入口，控制生成数量和分布
├── style_profile.json       — 阶段A产出的样式画像
├── templates/
│   ├── page_layouts.py      — 页面布局模板（单列/双列/三列/仪表盘）
│   ├── button.py            — 按钮生成器（基于样式画像）
│   ├── input.py             — 输入框生成器
│   ├── form.py              — 表单组合（label+input+button 组合）
│   ├── table.py             — 表格生成器
│   ├── modal.py             — 弹窗/遮罩生成器
│   ├── dropdown.py          — 下拉菜单生成器
│   ├── navbar.py            — 导航栏生成器
│   ├── card.py              — 卡片生成器
│   ├── toolbar.py           — 工具栏/操作栏
│   ├── pagination.py        — 分页组件
│   ├── overlay.py           — 遮盖层（loading遮罩、确认弹窗、cookie提示）
│   └── backgrounds.py       — 背景生成（纯色/渐变/网格/纹理）
├── renderer.py              — Playwright 渲染 HTML → 截图
├── labeler.py               — DOM 提取 bbox → YOLO txt
└── augment.py               — 后期图像增强（模拟不同环境）
```

### B2. 每次生成一张截图的流程

```
1. 随机选布局模板（40% 表单页 / 30% 列表页 / 20% 仪表盘 / 10% 登录页）
2. 填充元素：
   - 根据布局，在对应位置插入按钮、输入框、表格等
   - 每个元素的样式从样式画像中随机采样（颜色、大小、圆角等）
3. 添加噪音元素：
   - 10% 概率加一个弹窗/遮罩在最上层
   - 5% 概率加 tooltip 悬停在某元素上
   - 15% 概率加 toast 通知在角落
4. 生成 HTML，注入内联 CSS
5. Playwright 打开 HTML：
   - 随机视口大小（1366x768 ~ 1920x1080）
   - 25% 概率用暗色主题
   - 随机 deviceScaleFactor（1x / 1.5x / 2x，模拟不同显示器）
6. 截图 + 注入 JS 获取每个元素的 bbox
7. 输出：screenshot_00001.jpg + screenshot_00001.txt（YOLO 标注）
```

### B3. 各类元素的具体生成规则

#### 按钮 (button)

```python
def generate_button(style_profile):
    color = random.choice(style_profile["button_styles"]["common_colors"])
    size = random.choice(style_profile["button_styles"]["common_sizes"])
    border = random.choice(["solid", "dashed", "none", "outline-only"])
    text = random.choice(["提交", "确定", "取消", "搜索", "保存", "删除", "编辑", "新建",
                          "Submit", "OK", "Cancel", "Search", "Save", "Delete"])
    icon = random.choice([None, "left-icon", "right-icon", "icon-only"])
    state = random.choice(["normal", "disabled", "loading"])
    return ButtonHTML(color, size, border, text, icon, state)
```

生成的 HTML 示例（基于样式画像采样）：

```html
<button style="background:#1890ff;color:#fff;padding:4px 15px;
  font-size:14px;border-radius:6px;border:1px solid #1890ff;
  box-shadow:0 2px 0 rgba(5,145,255,0.1);">
  确定
</button>

<button style="background:transparent;color:#ff4d4f;padding:4px 15px;
  font-size:14px;border-radius:6px;border:1px solid #ff4d4f;">
  删除
</button>

<button style="opacity:0.4;cursor:not-allowed;background:#f5f5f5;
  color:rgba(0,0,0,0.25);padding:4px 15px;font-size:14px;
  border-radius:6px;border:1px solid #d9d9d9;" disabled>
  已禁用
</button>
```

#### 输入框 (input)

```python
def generate_input(style_profile):
    variant = random.choice(["default", "search", "password", "textarea", "number"])
    has_prefix = random.random() < 0.15  # 前辍图标
    has_suffix = random.random() < 0.10  # 后缀（单位、清空按钮）
    has_label = random.random() < 0.7    # 前面有 label
    has_error = random.random() < 0.08   # 错误状态（红色边框）
    placeholder = random.choice(["请输入", "搜索...", "", "请输入用户名", "Search..."])
    return InputHTML(variant, has_prefix, has_suffix, has_label, has_error, placeholder)
```

#### 弹窗/遮盖 (modal & overlay) — 重点

这是你特别关心的部分。遮盖分几类：

**类别 1：确认弹窗（最经典）**
```
z-index: 1000+ 居中白色卡片
背景半透明遮罩（rgba(0,0,0,0.45)）
标题 + 正文 + 确定/取消按钮
```
**类别 2：抽屉/侧边栏弹出**
```
从右侧滑入的面板
z-index 高，覆盖内容区
有 title + 关闭按钮
```
**类别 3：Loading 遮罩**
```
全屏半透明 + 居中 spinner
按钮上覆盖 loading 图标
```
**类别 4：Cookie/隐私提示条**
```
底部固定条
有"接受"/"拒绝"按钮
```
**类别 5：Toast 通知**
```
右上角/顶部居中浮出
2-3 秒自动消失
success/error/warning/info
```
**类别 6：Tooltip/Hover 卡片**
```
鼠标悬浮时出现的小气泡
紧挨目标元素
```

对于遮盖元素，YOLO 标注时有两种策略：
- **策略 A**：把遮盖层也标注为一个类别（如 `modal`、`overlay`），让模型学会识别"当前有弹窗"
- **策略 B**：遮盖下的元素不标注，只标注遮盖层和遮盖层上的按钮。因为遮盖下的按钮不可交互。

**推荐策略 B**：因为你的目标是"模拟操作"，遮盖下的元素点不了，不需要标注。

### B4. 数据分布控制

不是平均分配，要模拟真实网页的元素频率：

```
按钮（button）：    25%   ← 最常见
输入框（input）：   20%   ← 第二常见
链接（link）：      15%
图标（icon）：      12%
下拉框（select）：   8%
复选/单选：         7%
文本域（textarea）： 5%
弹窗（modal）：      5%   ← 低频但重要
遮盖（overlay）：    3%   ← 同上
```

每张图 3-8 个元素，总共生成 3000-5000 张，最终元素实例数：

```
按钮：约 3000-4500 个实例
输入框：约 2400-3600 个
弹窗：约 600-900 个（足够模型学会）
遮盖：约 360-540 个
```

### B5. 后期增强（模拟截图不完美的情况）

截图后再加一层图像增强，模拟真实环境的"脏"：

```
1. JPEG 压缩伪影（quality 70-95 随机）
   → 模拟截图工具压缩
2. 轻微色彩偏移（HSV 随机 ±5%）
   → 模拟不同显示器色差
3. 轻微模糊（Gaussian σ=0-1.0）
   → 模拟窗口未聚焦/缩放
4. 随机噪点（强度 0-3%，15% 概率）
   → 模拟低分辨率屏幕
5. 轻微透视变形（5% 概率）
   → 模拟屏幕拍照（如果以后需要支持手机拍照场景）
6. 窗口装饰（可选，10% 概率）
   → 模拟截图中包含浏览器工具栏
```

---

## C. 执行计划

### 第一步：收集阶段（Hermes 做）

- 选 10-15 个目标网站
- 逐个访问，提取 DOM + 截图
- 分析所有元素样式，输出 `style_profile.json`
- 预计耗时：约 30-60 分钟

### 第二步：编码阶段

根据 `style_profile.json` 写生成器代码
- `templates/` 下的每个模块
- `renderer.py` 和 `labeler.py`
- 测试生成 50 张，检查标注质量
- 预计耗时：写代码 2-3 小时

### 第三步：生成阶段

- 生成 3000 张合成数据
- 生成 300 张弹窗/遮盖专项数据
- 自动跑，不需要人工干预
- 预计耗时：生成 30 分钟（自动）

### 第四步：训练阶段

- YOLO11s 微调
- 50-80 epochs
- 预计耗时：30-60 分钟（GTX 1060）

---

## D. 评判标准

合成数据质量检验，生成完后抽查 100 张：

```
✅ 元素完整可见（没有被意外裁切）
✅ 标注框精准（和元素边界吻合，误差 < 3px）
✅ 样式多样（不是千篇一律的颜色和大小）
✅ 遮盖层正确（弹窗在上层，遮罩半透明）
✅ 暗色主题也有覆盖
✅ 类目平衡（没有某类元素太少）
```

---

## E. 和 GPT 原方案的本质区别

| | GPT 方案 | 本方案 |
|---|---|---|
| 数据来源 | 找别人标注好的数据集 | **先抓真实网页→分析规律→模仿生成** |
| 标注 | 依赖现成/手动 | **DOM 自动提取，100% 准确** |
| 遮盖处理 | 没提 | **专门设计弹窗/遮罩生成逻辑** |
| 多样性 | 受限于数据集 | **样式画像驱动，理论上无限** |
| 可控性 | 低（别人标了什么就是什么） | **高（想加什么类型元素随时加）** |

---

## F. 云主机训练操作流程

### 为什么用云主机

- 本机 GTX 1060 6G 训练 YOLO11s 勉强，训不了 YOLO11m
- 青椒云 RTX 3090（24G 显存）¥1.06/小时，训完关机，总花费 ¥2-5

### 操作步骤

```
第 1 步：买云主机
  青椒云 → 选"3090进阶版-24G" → Ubuntu 镜像 → 按时计费 → 开机

第 2 步：SSH 登录，装环境（一次性，10 分钟）
  sudo apt update && sudo apt install -y python3-pip
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
  pip install ultralytics

第 3 步：上传合成数据
  # 在你的本机打包
  tar -czf yolo_ui_data.tar.gz yolo_ui_dataset/

  # scp 上传到云主机
  scp yolo_ui_data.tar.gz root@<云主机IP>:~/

  # 云主机上解压
  tar -xzf yolo_ui_data.tar.gz

第 4 步：训练（10-30 分钟）
  yolo detect train \
    model=yolov11s.pt \
    data=yolo_ui_dataset/data.yaml \
    epochs=80 \
    imgsz=640 \
    batch=16 \
    device=0

第 5 步：导出 ONNX
  yolo export model=runs/detect/train/weights/best.pt format=onnx

第 6 步：下载模型 + 关机
  scp root@<云主机IP>:~/runs/detect/train/weights/best.onnx ./
  # 关机！别忘了，不然一直扣费
```

### 费用预估

| 步骤 | 耗时 | 费用 |
|------|------|------|
| 装环境 | 10 分钟 | ¥0.18 |
| 上传数据 | 2 分钟 | ¥0.04 |
| 训练 | 15-30 分钟 | ¥0.27-0.53 |
| 导出+下载 | 5 分钟 | ¥0.09 |
| **合计** | **约 1 小时** | **¥1.06 封顶** |

---

## G. 微调原理（为什么 COCO 预训练 + 合成数据可行）

很多同学混淆"预训练权重"和"现成数据集"：

```
YOLO11s.pt 是怎么来的？
  └─ Ultralytics 在 COCO 数据集上训练的
     COCO = 自然场景（人、车、猫狗、椅子...）
     不是网页 UI！

它学到了什么？
  ✅ 边缘、圆角、矩形、阴影、文字区域
  ✅ 什么是"前景物体" vs "背景"
  ❌ 不知道"按钮"长什么样
  ❌ 不知道"弹窗"是什么

你的合成数据做什么？
  → 教它："你认识的那些矩形，这个叫 button"
  → "半透明遮罩加白框叫 modal"
  → "这个有下拉箭头的小矩形叫 select"
```

所以微调 = COCO 提供的视觉基础 + 合成数据提供的 UI 语义 = 你的模型。

**和 GPT 方案的本质区别：**
- GPT 方案：拿别人标好的 UI 数据集，类别固定，不能加弹窗
- 我们的方案：自定类别、自控数据、想加什么类型随时加

---

## H. 弹框/遮盖的识别策略

### 不透明弹框

弹框完全遮住下面元素时，被遮元素 YOLO 看不到 → 不需要标注。不影响自动化，因为被遮住的你也点不了。

标注策略：
- ✓ 弹框本身 → class: modal
- ✓ 弹框上的按钮 → class: button（在弹框 z-index 上方）
- ✓ 弹框外可见元素 → 正常标注
- ✗ 被弹框完全遮住的元素 → 不标注

### 半透明遮罩

遮罩下面元素隐约可见。需要在训练数据中包含半透明遮罩样本。

```
生成器加 rgba(0,0,0,0.3) 遮罩层
→ YOLO 学习"遮罩下面可能还有元素"
→ 推理时识别出 overlay + 下面元素
→ 自动化逻辑判断：检测到 overlay → 忽略其覆盖区域的元素
```

标注两层：遮罩 → overlay，弹窗卡片 → modal，弹窗内按钮 → button。

---

## I. 后期测试与迭代改进

### 测试流程

```
1. 准备验证集（200张真实网页截图 + 手动标注）
   → 从实际要操作的网页截取
   → 不参与训练，纯测试

2. 跑指标
   yolo val model=best.pt data=val_data.yaml

3. 核心指标
   mAP@0.5      > 0.8（整体检测质量）
   Recall       > 0.85（漏检率，自动化最怕漏元素）
   中心点命中率  > 85%（点下去能点到）

4. 实际使用测试
   → 替换截图流程中的 OpenCV
   → 跑 50 个真实操作场景
   → 统计误点击、漏元素次数
```

### 改进循环（核心）

```
训练初始模型 → 实际使用收集错误 → 分析错误类型
    ↑                                        ↓
    └── 重新微调 30 epochs ←── 针对性补充数据

每轮 30 分钟，3-5 轮 mAP 从 0.6 拉到 0.9+
```

常见错误类型和补救：
- 漏检某类元素 → 多生成该类 200 张
- 暗色模式差 → 多生成暗色数据
- 弹窗场景差 → 多生成弹窗数据
- 小元素漏检 → 提高 tile overlap

---

## J. 本机低成本试跑（推荐先做）

**强烈建议：上云花钱前，先在本地用 YOLO11n 验证整个流程。**

### 试跑方案

```
模型:    YOLO11n（nano，2.6M 参数，5MB）
数据:    200-300 张合成数据
训练:    GTX 1060，batch=4，30 epochs
时间:    约 15-20 分钟
显存:    约 2-3GB（轻松）
目标:    mAP@0.5 > 0.6 即方案可行
```

### 为什么先试跑

| 直接上云 | 先本机试跑 |
|---------|-----------|
| 数据格式错 → 白花 ¥2 | 格式错 → 零成本修正 |
| 类别定义不对 → 重新来 | 类别不对 → 快速调整 |
| 心里没底 | 心里有底，上云就是放大版 |

### 试跑步骤

```bash
# 1. 装环境（WSL 里装）
pip install torch torchvision
pip install ultralytics

# 2. 生成 200 张合成数据（生成器产出）

# 3. 训练
yolo detect train \
  model=yolov11n.pt \
  data=data.yaml \
  epochs=30 \
  imgsz=640 \
  batch=4 \
  device=0

# 4. 评估
yolo val model=runs/detect/train/weights/best.pt data=data.yaml

# 5. 如果 mAP@0.5 > 0.6 → 方案可行 → 上云训大的
#    如果 mAP@0.5 < 0.4 → 调整数据/类别 → 本机再试
```

---

## 下一步

阶段 A/B 已完成（样式画像产出）。接下来写合成数据生成器代码，先产出 200 张给本机试跑。
