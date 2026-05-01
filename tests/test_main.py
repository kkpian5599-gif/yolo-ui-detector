"""Tests for generator.main command-line behavior."""
import sys
from pathlib import Path

import generator.main as generator_main


class _FakeSession:
    def stop(self):
        pass


def _stub_generation(monkeypatch):
    monkeypatch.setattr(generator_main, "get_session", lambda: _FakeSession())
    monkeypatch.setattr(
        generator_main,
        "generate_page",
        lambda: ("<html></html>", 100, 100, {}),
    )
    monkeypatch.setattr(generator_main, "assign_split", lambda index: "train")

    def fake_render_page(html, width, height, output_dir, index, session=None):
        img = output_dir / "images" / f"{index:05d}.jpg"
        img.parent.mkdir(parents=True, exist_ok=True)
        img.write_bytes(f"image-{index}".encode("ascii"))
        return str(img), [
            {
                "tag": "button",
                "type": "",
                "className": "",
                "text": "OK",
                "x": 1,
                "y": 1,
                "w": 10,
                "h": 10,
            }
        ]

    def fake_generate_labels(bboxes, width, height, output_dir, index, split="train"):
        label = output_dir / "labels" / split / f"{index:05d}.txt"
        label.parent.mkdir(parents=True, exist_ok=True)
        label.write_text("0 0.5 0.5 0.1 0.1", encoding="utf-8")
        return 1, 0

    monkeypatch.setattr(generator_main, "render_page", fake_render_page)
    monkeypatch.setattr(generator_main, "generate_labels", fake_generate_labels)
    monkeypatch.setattr(
        generator_main,
        "generate_data_yaml",
        lambda output_dir, classes: output_dir / "data.yaml",
    )


def test_output_dir_option_writes_smoke_data_outside_default_dataset(tmp_path, monkeypatch):
    _stub_generation(monkeypatch)
    project_root = tmp_path / "project"
    smoke_dir = tmp_path / "dataset_smoke"
    monkeypatch.setattr(generator_main, "ROOT", project_root)
    monkeypatch.setattr(
        sys,
        "argv",
        ["generator.main", "--count", "1", "--start", "0", "--output-dir", str(smoke_dir)],
    )

    generator_main.main()

    assert (smoke_dir / "images" / "train" / "00000.jpg").exists()
    assert (smoke_dir / "labels" / "train" / "00000.txt").exists()
    assert not (project_root / "dataset" / "images" / "train" / "00000.jpg").exists()


def test_existing_split_image_is_replaced_when_start_is_reused(tmp_path, monkeypatch):
    _stub_generation(monkeypatch)
    dataset = tmp_path / "dataset"
    old_img = dataset / "images" / "train" / "00000.jpg"
    old_img.parent.mkdir(parents=True, exist_ok=True)
    old_img.write_bytes(b"old-image")
    monkeypatch.setattr(generator_main, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["generator.main", "--count", "1", "--start", "0"])

    generator_main.main()

    assert old_img.read_bytes() == b"image-0"
    assert (dataset / "labels" / "train" / "00000.txt").exists()
