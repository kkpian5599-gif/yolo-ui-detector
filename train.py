"""
train.py — 生成合成数据集 + 立即启动 YOLOv8 训练

用法:
  python train.py                          # 默认生成 500 张，跑 100 epoch
  python train.py --count 1000 --epochs 150
  python train.py --skip-gen              # 跳过生成，直接用已有数据训练
  python train.py --count 500 --model yolov8s.pt  # 指定基础模型
"""
import sys
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent


def parse_args():
    p = argparse.ArgumentParser(description="Generate dataset + train YOLO")
    p.add_argument("--count",     type=int,   default=500,          help="生成图片数量")
    p.add_argument("--epochs",    type=int,   default=100,          help="训练 epoch 数")
    p.add_argument("--model",     type=str,   default="yolo11m.pt", help="基础模型权重")
    p.add_argument("--imgsz",     type=int,   default=640,          help="训练图像尺寸")
    p.add_argument("--batch",     type=int,   default=16,           help="batch size")
    p.add_argument("--workers",   type=int,   default=4,            help="DataLoader 工作线程数")
    p.add_argument("--device",    type=str,   default="",           help="训练设备，如 0 或 cpu")
    p.add_argument("--name",      type=str,   default="yolo_ui",    help="训练任务名称")
    p.add_argument("--skip-gen",  action="store_true",              help="跳过数据生成步骤")
    return p.parse_args()


def run_generation(count: int):
    print(f"\n{'='*60}")
    print(f"  STEP 1 / 2 — 生成合成数据集 ({count} 张)")
    print(f"{'='*60}\n")
    result = subprocess.run(
        [sys.executable, "-m", "generator.main", "--count", str(count)],
        cwd=str(ROOT),
    )
    if result.returncode != 0:
        print("\n[ERROR] 数据生成失败，中止。")
        sys.exit(1)


def run_training(args):
    print(f"\n{'='*60}")
    print(f"  STEP 2 / 2 — 启动 YOLOv8 训练")
    print(f"{'='*60}\n")

    data_yaml = ROOT / "dataset" / "data.yaml"
    if not data_yaml.exists():
        print(f"[ERROR] 找不到 {data_yaml}，请先生成数据集。")
        sys.exit(1)

    # 检查训练/验证集是否非空
    train_dir = ROOT / "dataset" / "images" / "train"
    val_dir   = ROOT / "dataset" / "images" / "val"
    n_train   = len(list(train_dir.glob("*.jpg"))) if train_dir.exists() else 0
    n_val     = len(list(val_dir.glob("*.jpg")))   if val_dir.exists()   else 0
    print(f"  数据集: {n_train} train / {n_val} val")

    if n_train == 0:
        print("[ERROR] train 集为空，请先生成数据。")
        sys.exit(1)
    if n_val == 0:
        print("[WARN]  val 集为空，训练可继续但无法评估 mAP。")

    # 构造 ultralytics 训练命令
    cmd = [
        sys.executable, "-m", "ultralytics", "train",
        f"data={data_yaml}",
        f"model={args.model}",
        f"epochs={args.epochs}",
        f"imgsz={args.imgsz}",
        f"batch={args.batch}",
        f"workers={args.workers}",
        f"name={args.name}",
        f"project={ROOT / 'runs'}",
    ]
    if args.device:
        cmd.append(f"device={args.device}")

    print("  命令:", " ".join(cmd))
    print()
    result = subprocess.run(cmd, cwd=str(ROOT))
    if result.returncode != 0:
        print("\n[ERROR] 训练失败。")
        sys.exit(1)

    print(f"\n[OK] 训练完成！结果保存在: {ROOT / 'runs' / args.name}")


def main():
    args = parse_args()

    if not args.skip_gen:
        run_generation(args.count)

    run_training(args)


if __name__ == "__main__":
    main()
