"""YOLO标注文件生成器"""
import json
from pathlib import Path
from .renderer import map_to_class


def generate_labels(bboxes: list, img_width: int, img_height: int, output_dir: Path, index: int):
    """
    将 Playwright 提取的 bbox 转为 YOLO 格式

    bbox格式: {tag, type, text, className, x, y, w, h}
    YOLO格式: class_id x_center y_center width height（全部归一化到0-1）
    """
    labels_dir = output_dir / "labels"
    labels_dir.mkdir(parents=True, exist_ok=True)

    label_path = labels_dir / f"{index:05d}.txt"
    lines = []
    skipped = 0

    for bbox in bboxes:
        class_id = map_to_class(
            bbox.get("tag", ""),
            bbox.get("type", ""),
            bbox.get("className", ""),
            bbox.get("text", ""),
        )
        if class_id < 0:
            skipped += 1
            continue

        # 归一化坐标
        x_center = (bbox["x"] + bbox["w"] / 2) / img_width
        y_center = (bbox["y"] + bbox["h"] / 2) / img_height
        w_norm = bbox["w"] / img_width
        h_norm = bbox["h"] / img_height

        # 裁剪到 [0,1]
        x_center = max(0, min(1, x_center))
        y_center = max(0, min(1, y_center))
        w_norm = max(0, min(1, w_norm))
        h_norm = max(0, min(1, h_norm))

        lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}")

    label_path.write_text("\n".join(lines), encoding="utf-8")
    return len(lines), skipped


def generate_data_yaml(output_dir: Path, classes: list):
    """生成 data.yaml 训练配置文件"""
    yaml_path = output_dir / "data.yaml"
    names_yaml = "\n".join(f"  - {c}" for c in classes)
    content = f"""# YOLO training config (auto-generated)
path: {output_dir.as_posix()}
train: images
val: images

nc: {len(classes)}
names:
{names_yaml}
"""
    yaml_path.write_text(content, encoding="utf-8")
    return yaml_path
