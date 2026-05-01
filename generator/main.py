"""合成数据生成入口 — python -m generator.main [数量]

优化项：
  #2  images/train 和 images/val 独立子目录
  #8  持久化 BrowserSession，全流程复用同一个 Browser/Page
"""
import sys
from pathlib import Path

from .config import ROOT, CLASSES, NUM_CLASSES
from .templates.page import generate_page
from .renderer import render_page, get_session, BrowserSession
from .labeler import generate_labels, generate_data_yaml, assign_split


def main():
    count = 200
    start_override = None  # None = 自动检测

    args = sys.argv[1:]
    positional = []
    i = 0
    while i < len(args):
        if args[i] == "--start" and i + 1 < len(args):
            try:
                start_override = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif args[i] == "--count" and i + 1 < len(args):
            try:
                count = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            positional.append(args[i])
            i += 1

    if positional:
        try:
            count = int(positional[0])
        except ValueError:
            pass

    output_dir  = ROOT / "dataset"
    # train/val 图片子目录 (#2)
    train_img_dir = output_dir / "images" / "train"
    val_img_dir   = output_dir / "images" / "val"
    train_img_dir.mkdir(parents=True, exist_ok=True)
    val_img_dir.mkdir(parents=True, exist_ok=True)

    # 自动续传：检测已有图片总数（train + val），接着往后生成
    if start_override is not None:
        start = start_override
        print(f"Manual start override: #{start}")
    else:
        existing = (
            len(list(train_img_dir.glob("*.jpg"))) +
            len(list(val_img_dir.glob("*.jpg")))
        )
        if existing > 0:
            print(f"Found {existing} existing images, resuming from #{existing}")
        start = existing

    end = start + count
    print(f"Generating {count} synthetic pages (#{start} -> #{end-1}) -> {output_dir}")
    print(f"Classes: {CLASSES}")

    total_labels = 0
    n_train = 0
    n_val   = 0

    # 持久化 Browser (#8)
    session: BrowserSession = get_session()

    try:
        for i in range(start, end):
            try:
                html, width, height, _meta = generate_page()

                # 决定 train/val split (#2)
                split = assign_split(i)
                split_img_dir = output_dir / "images" / split
                split_img_dir.mkdir(parents=True, exist_ok=True)

                img_path, bboxes = render_page(
                    html, width, height, output_dir, i, session=session
                )

                # 把截图移到对应 split 子目录
                from pathlib import Path as _P
                src = _P(img_path)
                dst = split_img_dir / src.name
                if src != dst:
                    src.rename(dst)

                n_labels, _ = generate_labels(
                    bboxes, width, height, output_dir, i, split=split
                )
                total_labels += n_labels
                if split == "train":
                    n_train += 1
                else:
                    n_val += 1

                if (i - start + 1) % 20 == 0:
                    print(
                        f"  [{i - start + 1:4d}/{count}] img#{i:05d} "
                        f"({split:5s}) {n_labels} labels | total: {total_labels}"
                    )
            except KeyboardInterrupt:
                raise
            except Exception as e:
                import traceback
                print(f"  [{i - start + 1:4d}/{count}] img#{i:05d} ERROR: {e}")
                traceback.print_exc()

    except KeyboardInterrupt:
        print(f"\n  Interrupted")
    finally:
        session.stop()

    generate_data_yaml(output_dir, CLASSES)
    print(f"\nDone! {count} images ({n_train} train / {n_val} val), {total_labels} labels")
    print(f"  {output_dir / 'images' / 'train'}  - train screenshots")
    print(f"  {output_dir / 'images' / 'val'}    - val screenshots")
    print(f"  {output_dir / 'labels' / 'train'}  - train YOLO annotations")
    print(f"  {output_dir / 'labels' / 'val'}    - val YOLO annotations")
    print(f"  {output_dir / 'data.yaml'}         - train config")


if __name__ == "__main__":
    main()
