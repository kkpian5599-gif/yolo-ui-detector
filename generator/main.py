"""合成数据生成入口 — python -m generator.main [数量]"""
import sys
from pathlib import Path
from .config import ROOT, CLASSES, NUM_CLASSES
from .templates.page import generate_page
from .renderer import render_page
from .labeler import generate_labels, generate_data_yaml


def main():
    count = 200
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass

    output_dir = ROOT / "dataset"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {count} synthetic pages -> {output_dir}")
    print(f"Classes: {CLASSES}")

    total_labels = 0
    for i in range(count):
        try:
            html, width, height, _meta = generate_page()
            img_path, bboxes = render_page(html, width, height, output_dir, i)
            n_labels, _ = generate_labels(bboxes, width, height, output_dir, i)
            total_labels += n_labels

            if (i + 1) % 20 == 0:
                print(f"  [{i+1:4d}/{count}] {n_labels} labels | total: {total_labels}")
        except Exception as e:
            print(f"  [{i+1:4d}/{count}] ERROR: {e}")

    generate_data_yaml(output_dir, CLASSES)
    print(f"Done! {count} images, {total_labels} labels")
    print(f"  {output_dir / 'images'}  - screenshots")
    print(f"  {output_dir / 'labels'}  - YOLO annotations")
    print(f"  {output_dir / 'data.yaml'} - train config")


if __name__ == "__main__":
    main()
