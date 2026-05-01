"""Test labeler: YOLO format generation and data.yaml creation

P1修复：generate_labels 增加了 split= 参数，输出路径为 labels/train/ 或 labels/val/
"""
import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.labeler import generate_labels, generate_data_yaml, assign_split


class TestGenerateLabels:
    def test_basic_label_generation(self):
        bboxes = [
            {"tag": "button", "type": "", "className": "", "text": "OK",
             "yoloClass": "", "x": 100, "y": 200, "w": 80, "h": 32},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, skipped = generate_labels(bboxes, 1920, 1080, out, 0, split="train")

            assert n_labels == 1
            assert skipped == 0

            # Phase 1: 路径改为 labels/train/
            label_file = out / "labels" / "train" / "00000.txt"
            assert label_file.exists(), f"Expected {label_file} to exist"
            content = label_file.read_text()
            parts = content.strip().split()
            assert len(parts) == 5
            # class_id should be 0 (button)
            assert parts[0] == "0"
            # Check normalized center coordinates
            cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            assert 0 <= cx <= 1
            assert 0 <= cy <= 1
            assert 0 <= w <= 1
            assert 0 <= h <= 1

    def test_modal_via_yolo_class_attr(self):
        """data-yolo-class='modal' should map to class 8"""
        bboxes = [
            {"tag": "div", "type": "", "className": "", "text": "",
             "yoloClass": "modal", "x": 0, "y": 0, "w": 1920, "h": 1080},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, skipped = generate_labels(bboxes, 1920, 1080, out, 0, split="train")

            assert n_labels == 1
            label_file = out / "labels" / "train" / "00000.txt"
            content = label_file.read_text()
            assert content.strip().split()[0] == "8"

    def test_modal_via_classname(self):
        """className 含 'modal-overlay' 也映射到 class 8"""
        bboxes = [
            {"tag": "div", "type": "", "className": "modal-overlay", "text": "",
             "yoloClass": "", "x": 0, "y": 0, "w": 1920, "h": 1080},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, _ = generate_labels(bboxes, 1920, 1080, out, 0, split="train")
            assert n_labels == 1
            label_file = out / "labels" / "train" / "00000.txt"
            assert label_file.read_text().strip().split()[0] == "8"

    def test_unknown_tag_skipped(self):
        bboxes = [
            {"tag": "div", "type": "", "className": "", "text": "hello",
             "yoloClass": "", "x": 100, "y": 100, "w": 50, "h": 50},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, skipped = generate_labels(bboxes, 1920, 1080, out, 0, split="train")

            assert n_labels == 0
            assert skipped == 1

    def test_multiple_bboxes(self):
        bboxes = [
            {"tag": "button", "type": "", "className": "", "text": "A",
             "yoloClass": "", "x": 10, "y": 10, "w": 40, "h": 20},
            {"tag": "button", "type": "", "className": "", "text": "B",
             "yoloClass": "", "x": 100, "y": 10, "w": 40, "h": 20},
            {"tag": "input", "type": "text", "className": "", "text": "",
             "yoloClass": "", "x": 200, "y": 10, "w": 120, "h": 30},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, skipped = generate_labels(bboxes, 640, 480, out, 0, split="train")

            assert n_labels == 3
            assert skipped == 0

            label_file = out / "labels" / "train" / "00000.txt"
            lines = label_file.read_text().strip().split("\n")
            assert len(lines) == 3

    def test_out_of_bounds_clipped(self):
        """Labels with coords outside [0,1] should be clipped"""
        bboxes = [
            {"tag": "button", "type": "", "className": "", "text": "X",
             "yoloClass": "", "x": -100, "y": -100, "w": 50, "h": 50},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, _ = generate_labels(bboxes, 640, 480, out, 0, split="train")
            assert n_labels == 1

            label_file = out / "labels" / "train" / "00000.txt"
            content = label_file.read_text()
            parts = content.strip().split()
            cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            assert cx >= 0
            assert cy >= 0

    def test_val_split_uses_val_dir(self):
        """split='val' should write to labels/val/"""
        bboxes = [
            {"tag": "button", "type": "", "className": "", "text": "OK",
             "yoloClass": "", "x": 0, "y": 0, "w": 10, "h": 10},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            generate_labels(bboxes, 100, 100, out, 5, split="val")
            assert (out / "labels" / "val" / "00005.txt").exists()

    def test_label_filename_padding(self):
        bboxes = [{"tag": "button", "type": "", "className": "", "text": "OK",
                   "yoloClass": "", "x": 0, "y": 0, "w": 10, "h": 10}]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            generate_labels(bboxes, 100, 100, out, 42, split="train")
            assert (out / "labels" / "train" / "00042.txt").exists()

    def test_yolo_coords_normalized(self):
        """所有坐标必须严格在 [0,1]"""
        bboxes = [
            {"tag": "input", "type": "text", "className": "", "text": "",
             "yoloClass": "", "x": 50, "y": 30, "w": 200, "h": 40},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            generate_labels(bboxes, 640, 480, out, 0, split="train")
            label_file = out / "labels" / "train" / "00000.txt"
            for val in [float(v) for v in label_file.read_text().strip().split()[1:]]:
                assert 0.0 <= val <= 1.0, f"Coord {val} out of [0,1]"


class TestAssignSplit:
    def test_split_returns_train_or_val(self):
        for i in range(100):
            result = assign_split(i)
            assert result in ("train", "val")

    def test_split_is_deterministic(self):
        """Same index always gives same split"""
        for i in range(50):
            assert assign_split(i) == assign_split(i)

    def test_val_ratio_roughly_correct(self):
        """~15% should be val (allow ±5% tolerance for 1000 samples)"""
        results = [assign_split(i) for i in range(1000)]
        val_count = results.count("val")
        assert 100 <= val_count <= 200, f"val count={val_count}, expected ~150"


class TestGenerateDataYaml:
    def test_yaml_content(self):
        classes = ["button", "input", "checkbox", "radio", "select",
                   "textarea", "link", "icon", "modal"]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            path = generate_data_yaml(out, classes)

            assert path.exists()
            content = path.read_text()
            assert "nc: 9" in content
            assert "button" in content
            assert "modal" in content
            assert "train:" in content
            assert "val:" in content

    def test_yaml_has_names_list(self):
        classes = ["a", "b", "c"]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            path = generate_data_yaml(out, classes)

            content = path.read_text()
            assert "names:" in content
            assert "  - a" in content
            assert "  - b" in content
            assert "  - c" in content

    def test_yaml_path_field(self):
        """data.yaml 应包含正确的 path 字段"""
        classes = ["button"]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            path = generate_data_yaml(out, classes)
            content = path.read_text()
            assert "path:" in content
            assert "images/train" in content
            assert "images/val" in content
