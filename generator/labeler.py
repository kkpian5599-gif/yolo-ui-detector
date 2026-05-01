"""YOLO标注文件生成器

优化项：
  #1  IoU 去重：重叠率 > 0.65 时保留面积小的（控件本体），丢弃外层容器
  #2  train/val 自动划分：按 VAL_RATIO 比例写入独立子目录
"""
import json
import random
from pathlib import Path

from .renderer import map_to_class, compute_iou
from .config import VAL_RATIO


def _iou_dedup(raw_boxes: list, iou_thresh: float = 0.65) -> list:
    """
    对同一张图内的 bbox 做 IoU 去重。
    策略：两个 box IoU > thresh 时，保留面积更小的（控件本体 < 外层容器）。
    """
    boxes = sorted(raw_boxes, key=lambda b: b["w"] * b["h"])  # 小面积优先
    kept = []
    for box in boxes:
        overlap = False
        for k in kept:
            if compute_iou(box, k) > iou_thresh:
                overlap = True
                break
        if not overlap:
            kept.append(box)
    return kept


def generate_labels(bboxes: list, img_width: int, img_height: int,
                    output_dir: Path, index: int,
                    split: str = "train"):
    """
    将 Playwright 提取的 bbox 转为 YOLO 格式并写文件。

    split: 'train' | 'val' — 决定写入哪个子目录。

    bbox 格式: {tag, type, text, className, yoloClass, x, y, w, h}
    YOLO 格式: class_id x_center y_center width height（全部归一化到 0-1）
    """
    labels_dir = output_dir / "labels" / split
    labels_dir.mkdir(parents=True, exist_ok=True)

    label_path = labels_dir / f"{index:05d}.txt"
    lines = []
    skipped = 0

    # Step 1: 映射类别，过滤 -1
    typed_boxes = []
    for bbox in bboxes:
        class_id = map_to_class(
            bbox.get("tag", ""),
            bbox.get("type", ""),
            bbox.get("className", ""),
            bbox.get("text", ""),
            bbox.get("yoloClass", ""),   # #9
        )
        if class_id < 0:
            skipped += 1
            continue
        typed_boxes.append({**bbox, "_class_id": class_id})

    # Step 2: IoU 去重 (#1)
    deduped = _iou_dedup(typed_boxes)
    skipped += len(typed_boxes) - len(deduped)

    # Step 3: 归一化并写文件
    for bbox in deduped:
        x_center = (bbox["x"] + bbox["w"] / 2) / img_width
        y_center = (bbox["y"] + bbox["h"] / 2) / img_height
        w_norm   = bbox["w"] / img_width
        h_norm   = bbox["h"] / img_height

        # 裁剪到 [0, 1]
        x_center = max(0.0, min(1.0, x_center))
        y_center = max(0.0, min(1.0, y_center))
        w_norm   = max(0.0, min(1.0, w_norm))
        h_norm   = max(0.0, min(1.0, h_norm))

        lines.append(
            f"{bbox['_class_id']} {x_center:.6f} {y_center:.6f} "
            f"{w_norm:.6f} {h_norm:.6f}"
        )

    label_path.write_text("\n".join(lines), encoding="utf-8")
    return len(lines), skipped


def assign_split(index: int, val_ratio: float = VAL_RATIO) -> str:
    """
    为指定 index 分配 'train' 或 'val'。
    使用伪随机（以 index 为种子）保证同一 index 始终落入同一 split。
    """
    rng = random.Random(index)
    return "val" if rng.random() < val_ratio else "train"


def generate_data_yaml(output_dir: Path, classes: list):
    """生成 data.yaml 训练配置文件（含独立 train/val 目录）"""
    yaml_path = output_dir / "data.yaml"
    names_yaml = "\n".join(f"  - {c}" for c in classes)
    content = f"""# YOLO training config (auto-generated)
path: {output_dir.as_posix()}
train: images/train
val:   images/val

nc: {len(classes)}
names:
{names_yaml}
"""
    yaml_path.write_text(content, encoding="utf-8")
    return yaml_path
