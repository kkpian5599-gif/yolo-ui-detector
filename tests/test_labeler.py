"""Test labeler: YOLO format generation and data.yaml creation"""
import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.labeler import generate_labels, generate_data_yaml


class TestGenerateLabels:
    def test_basic_label_generation(self):
        bboxes = [
            {"tag": "button", "type": "", "className": "", "text": "OK",
             "x": 100, "y": 200, "w": 80, "h": 32},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, skipped = generate_labels(bboxes, 1920, 1080, out, 0)

            assert n_labels == 1
            assert skipped == 0

            label_file = out / "labels" / "00000.txt"
            assert label_file.exists()
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

    def test_modal_label_maps_to_class_8(self):
        bboxes = [
            {"tag": "div", "type": "", "className": "modal-overlay", "text": "",
             "x": 0, "y": 0, "w": 1920, "h": 1080},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, skipped = generate_labels(bboxes, 1920, 1080, out, 0)

            assert n_labels == 1
            assert skipped == 0

            label_file = out / "labels" / "00000.txt"
            content = label_file.read_text()
            assert content.strip().split()[0] == "8"

    def test_unknown_tag_skipped(self):
        bboxes = [
            {"tag": "div", "type": "", "className": "", "text": "hello",
             "x": 100, "y": 100, "w": 50, "h": 50},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, skipped = generate_labels(bboxes, 1920, 1080, out, 0)

            assert n_labels == 0
            assert skipped == 1

    def test_multiple_bboxes(self):
        bboxes = [
            {"tag": "button", "type": "", "className": "", "text": "A",
             "x": 10, "y": 10, "w": 40, "h": 20},
            {"tag": "button", "type": "", "className": "", "text": "B",
             "x": 100, "y": 10, "w": 40, "h": 20},
            {"tag": "input", "type": "text", "className": "", "text": "",
             "x": 200, "y": 10, "w": 120, "h": 30},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, skipped = generate_labels(bboxes, 640, 480, out, 0)

            assert n_labels == 3
            assert skipped == 0

            label_file = out / "labels" / "00000.txt"
            lines = label_file.read_text().strip().split("\n")
            assert len(lines) == 3

    def test_out_of_bounds_clipped(self):
        """Labels with coords outside [0,1] should be clipped"""
        bboxes = [
            {"tag": "button", "type": "", "className": "", "text": "X",
             "x": -100, "y": -100, "w": 50, "h": 50},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            n_labels, _ = generate_labels(bboxes, 640, 480, out, 0)
            assert n_labels == 1

            label_file = out / "labels" / "00000.txt"
            content = label_file.read_text()
            parts = content.strip().split()
            cx, cy, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
            assert cx >= 0
            assert cy >= 0

    def test_label_filename_padding(self):
        bboxes = [{"tag": "button", "type": "", "className": "", "text": "OK",
                    "x": 0, "y": 0, "w": 10, "h": 10}]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            generate_labels(bboxes, 100, 100, out, 42)
            assert (out / "labels" / "00042.txt").exists()


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
