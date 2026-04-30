"""Test modal, overlay, link, icon generation"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.templates.modal import (
    generate_modal_html,
    generate_overlay_html,
    generate_link_html,
    generate_icon_html,
)


class TestModal:
    def test_generate_modal_has_overlay_and_card(self):
        html, meta = generate_modal_html()
        assert "modal-overlay" in html
        assert "modal-card" in html
        assert meta["type"] == "modal"
        assert "title" in meta
        assert "dark" in meta

    def test_modal_has_buttons(self):
        html, _ = generate_modal_html()
        assert "modal-btn-ok" in html
        assert "modal-btn-cancel" in html

    def test_modal_has_fixed_position(self):
        html, _ = generate_modal_html()
        assert "position:fixed" in html

    def test_modal_titles_vary(self):
        titles = set()
        for _ in range(20):
            _, meta = generate_modal_html()
            titles.add(meta["title"])
        assert len(titles) >= 2

    def test_modal_dark_toggle(self):
        dark_count = 0
        for _ in range(50):
            _, meta = generate_modal_html()
            if meta["dark"]:
                dark_count += 1
        # With 20% probability, should see some dark modals
        assert dark_count >= 1


class TestOverlay:
    def test_generate_overlay(self):
        html, meta = generate_overlay_html()
        assert "overlay-area" in html
        assert meta["type"] == "overlay"
        assert "opacity" in meta
        assert 0.3 <= meta["opacity"] <= 0.6

    def test_overlay_has_position(self):
        html, _ = generate_overlay_html()
        assert "position:absolute" in html
        assert "rgba" in html


class TestLink:
    def test_generate_link(self):
        html, meta = generate_link_html()
        assert html.startswith("<a ")
        assert meta["type"] == "link"
        assert "text" in meta

    def test_link_has_href(self):
        html, _ = generate_link_html()
        assert 'href="' in html

    def test_link_texts_vary(self):
        texts = set()
        for _ in range(20):
            _, meta = generate_link_html()
            texts.add(meta["text"])
        assert len(texts) >= 2


class TestIcon:
    def test_generate_icon(self):
        html, meta = generate_icon_html()
        assert "<span" in html
        assert meta["type"] == "icon"
        assert "emoji" in meta
        assert "size" in meta

    def test_icon_sizes_in_range(self):
        for _ in range(20):
            _, meta = generate_icon_html()
            assert 16 <= meta["size"] <= 32

    def test_icons_vary(self):
        emojis = set()
        for _ in range(30):
            _, meta = generate_icon_html()
            emojis.add(meta["emoji"])
        assert len(emojis) >= 3
