"""Tests for full page layout generation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import generator.templates.page as page


def test_generate_page_can_render_icon_grid_layout(monkeypatch):
    def choose_first_or_icon_grid(options, weights=None):
        if "icon_grid" in options:
            return ["icon_grid"]
        if "fa" in options:
            return ["fa"]
        return [options[0]]

    monkeypatch.setattr(page.random, "choices", choose_first_or_icon_grid)
    monkeypatch.setattr(page.random, "random", lambda: 0.99)

    html, width, height, meta = page.generate_page()

    assert width > 0
    assert height > 0
    assert '<i class="fa-' in html
    assert any(item["type"] == "icon" for item in meta)
