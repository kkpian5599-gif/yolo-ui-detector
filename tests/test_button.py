"""Test button HTML generation"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.templates.button import (
    generate_button_html,
    random_button_style,
    _lighten,
    _tint,
    _lighter,
)


class TestButtonStyles:
    def test_random_button_style_returns_css_and_meta(self):
        style_css, color_name, style_type, size = random_button_style()
        assert isinstance(style_css, str)
        assert len(style_css) > 50
        assert "display" in style_css
        assert color_name in ("blue", "indigo", "purple", "green", "dark_green",
                              "yellow", "red", "gray")
        assert style_type in ("solid", "outline", "plain", "dashed", "round",
                              "text_only", "text_with_bg")
        assert size in ("small", "default", "large")

    def test_disabled_button_has_not_allowed_cursor(self):
        style_css, _, _, _ = random_button_style(disabled=True)
        assert "not-allowed" in style_css

    def test_enabled_button_has_pointer_cursor(self):
        style_css, _, _, _ = random_button_style(disabled=False)
        assert "pointer" in style_css
        assert "not-allowed" not in style_css

    def test_generate_button_html_returns_html_and_meta(self):
        html, meta = generate_button_html()
        assert html.startswith("<button")
        assert html.endswith("</button>")
        assert "style=" in html
        assert meta["type"] == "button"
        assert "text" in meta
        assert "disabled" in meta
        assert "color" in meta
        assert "style" in meta

    def test_generate_button_disabled(self):
        html, meta = generate_button_html(disabled=True)
        assert meta["disabled"] is True
        assert "not-allowed" in html

    def test_generate_button_not_disabled(self):
        html, meta = generate_button_html(disabled=False)
        assert meta["disabled"] is False
        assert "pointer" in html

    def test_buttons_have_random_texts(self):
        texts = set()
        for _ in range(30):
            _, meta = generate_button_html()
            texts.add(meta["text"])
        # Should have at least 3 different texts in 30 generations
        assert len(texts) >= 3

    def test_buttons_have_different_styles(self):
        styles = set()
        for _ in range(30):
            _, meta = generate_button_html()
            styles.add(meta["style"])
        # Should use multiple style types
        assert len(styles) >= 3


class TestColorHelpers:
    def test_lighten_makes_color_lighter(self):
        result = _lighten("#000000", factor=0.5)
        assert result == "#7f7f7f"

    def test_lighten_white_stays_white(self):
        result = _lighten("#ffffff", factor=0.5)
        assert result == "#ffffff"

    def test_tint_is_very_light(self):
        result = _tint("#0d6efd")
        # Should be very light (factor 0.85)
        assert result.startswith("#")
        r = int(result[1:3], 16)
        assert r > 200  # Very light

    def test_lighter_is_moderate(self):
        result = _lighter("#0d6efd")
        assert result.startswith("#")
        r = int(result[1:3], 16)
        assert 100 < r < 200  # Moderately light
