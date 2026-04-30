"""Test input/checkbox/radio/select/textarea HTML generation"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.templates.input import (
    generate_input_html,
    generate_checkbox_html,
    generate_radio_html,
    generate_select_html,
    generate_textarea_html,
)


class TestInput:
    def test_generate_input_returns_html_and_meta(self):
        html, meta = generate_input_html()
        assert "<input" in html
        assert meta["type"].startswith("input_")
        assert "size" in meta
        assert "disabled" in meta

    def test_input_types_vary(self):
        types = set()
        for _ in range(20):
            _, meta = generate_input_html()
            types.add(meta["type"])
        assert len(types) >= 2  # Should produce different input types

    def test_input_sizes_vary(self):
        sizes = set()
        for _ in range(20):
            _, meta = generate_input_html()
            sizes.add(meta["size"])
        assert len(sizes) >= 2

    def test_input_has_style(self):
        html, _ = generate_input_html()
        assert "style=" in html
        assert "width:" in html
        assert "border:" in html

    def test_label_appears_sometimes(self):
        """~70% of inputs should have a label"""
        with_label = 0
        for _ in range(50):
            html, _ = generate_input_html()
            if "<label" in html:
                with_label += 1
        # With 70% probability, 50 tries should have at least 20 with labels
        assert with_label >= 15


class TestCheckbox:
    def test_generate_checkbox(self):
        html, meta = generate_checkbox_html()
        assert '<input type="checkbox"' in html
        assert meta["type"] == "checkbox"
        assert "checked" in meta
        assert "disabled" in meta


class TestRadio:
    def test_generate_radio_has_multiple_options(self):
        html, meta = generate_radio_html()
        assert '<input type="radio"' in html
        assert meta["type"] == "radio"
        assert meta["count"] >= 2

    def test_radio_options_vary(self):
        for _ in range(10):
            html, _ = generate_radio_html()
            assert html.count("radio") >= 2  # At least 2 radio buttons


class TestSelect:
    def test_generate_select(self):
        html, meta = generate_select_html()
        assert "<select" in html
        assert "<option" in html
        assert meta["type"] == "select"
        assert meta["options"] >= 3

    def test_select_has_dropdown_arrow(self):
        html, _ = generate_select_html()
        assert "svg" in html  # Background image dropdown arrow


class TestTextarea:
    def test_generate_textarea(self):
        html, meta = generate_textarea_html()
        assert "<textarea" in html
        assert meta["type"] == "textarea"

    def test_textarea_has_placeholder(self):
        html, _ = generate_textarea_html()
        assert 'placeholder="' in html
