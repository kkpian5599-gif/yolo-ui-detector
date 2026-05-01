# YOLO UI Detector — 改进路线图

> 模型统一使用 `yolo11m.pt`（~20M 参数，RTX 3090 最优选择）
> 所有改进分批提交 GitHub，方便持续迭代

---

## 状态说明

| 符号 | 含义 |
|------|------|
| ✅   | 已完成并提交 |
| 🔧   | 进行中 |
| ⬜   | 待处理 |

---

## 🔴 Phase 1 — Bug 修复（高优先级，影响数据质量）

| # | 问题 | 文件 | 状态 |
|---|------|------|------|
| 1 | modal 内按钮（confirm/cancel）被 JS 选择器排除，导致这些 `button` 实例漏标注，降低 button 类别召回率 | `renderer.py` L24-35 | ✅ |
| 2 | `test_model.py` 扫图路径错误：`images/*.jpg` 但图在 `images/train/` 和 `images/val/` 子目录 | `test_model.py` L63 | ✅ |
| 3 | `train.py` 默认模型写死为 `yolov8n.pt`，与项目统一模型 `yolo11m.pt` 不一致 | `train.py` L22 | ✅ |
| 4 | `auto_train.sh` ONNX 导出路径缺 `/detect/` 子目录，`runs/${NAME}` 应为 `runs/detect/${NAME}` | `auto_train.sh` L154-158 | ✅ |

**提交策略**：Phase 1 一次提交 `fix: bug fixes for label coverage and model consistency`

---

## 🟡 Phase 2 — 数据增强补全（中优先级，提升鲁棒性）

| # | 问题 | 文件 | 状态 |
|---|------|------|------|
| 5 | `wait_for_timeout(400)` 改为 `wait_for_load_state('networkidle')`，防止字体图标未加载就截图 | `renderer.py` L163 | ✅ |
| 6 | Pillow 增强补全：高斯噪点（15%概率）、随机 JPEG 质量（70-95）| `renderer.py` `_augment_image()` | ✅ |
| 7 | 生成进度增加 ETA 估算（已用时 / 当前速度 → 剩余时间）| `main.py` | ✅ |

**提交策略**：Phase 2 一次提交 `feat: augmentation improvements and render reliability`

---

## 🟡 Phase 3 — 模板扩充（中优先级，提升样本多样性）

| # | 问题 | 文件 | 状态 |
|---|------|------|------|
| 8  | 新增 Toast 通知模板（右上角/顶部浮出，success/error/warning/info）| `templates/modal.py` | ✅ |
| 9  | 新增 Drawer 抽屉模板（右侧滑入侧边栏弹出）| `templates/modal.py` | ✅ |
| 10 | 新增 Table 页面布局（带 checkbox 的多行数据表格）| `templates/page.py` | ✅ |
| 11 | 新增 Navbar 导航栏组件（横向 logo+links+按钮）| `templates/page.py` | ✅ |
| 12 | `page.py` 随机加 toast（5%概率，和 modal 不同时）| `templates/page.py` | ✅ |

**提交策略**：Phase 3 一次提交 `feat: add toast/drawer/table/navbar templates`

---

## 🟢 Phase 4 — 工程质量（低优先级，长期维护）

| # | 问题 | 文件 | 状态 |
|---|------|------|------|
| 13 | 补充单元测试：验证 label 格式、YOLO 坐标范围、YAML 合法性 | `tests/` | ✅ |
| 14 | 补充内联 SVG icon 生成，让 icon 类别更接近真实网站 | `templates/modal.py` | ✅ |
| 15 | 训练完后自动运行 `test_model.py val` 输出 mAP | `auto_train.sh` | ✅ |

**提交策略**：Phase 4 逐条提交

---

## 模型参数对比（参考）

| 模型 | 参数量 | 大小 | 适用场景 |
|------|--------|------|---------|
| yolo11n | ~2.6M | 5MB | 本地快速验证 |
| yolo11s | ~9M   | 18MB | 本地小显存 |
| **yolo11m** | **~20M** | **40MB** | **RTX 3090 生产（当前选择）** |
| yolo11l | ~25M  | 50MB | 精度优先 |
| yolo11x | ~56M  | 110MB | 服务器旗舰 |

---

## 提交记录（自动追踪）

| 提交 | 内容 | 时间 |
|------|------|------|
| 96f971a | fix: make cloud training rerunnable | 2026-04-30 |
| 0ac28e8 | feat: epochs 100→150 for 5000 images | 2026-04-30 |
| cfc07ec | fix: default model yolo11s→yolo11m | 2026-04-30 |
| fb93c41 | refactor: 9-point optimization | 2026-04-29 |
