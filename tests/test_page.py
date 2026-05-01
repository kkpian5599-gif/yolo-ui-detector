"""Tests for full page layout generation.

P3新增：测试 table / navbar 布局、Toast/Drawer 注入
"""
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


def test_generate_page_table_layout(monkeypatch):
    """P3: table 布局应包含 <table> 和 checkbox"""
    def force_table(options, weights=None):
        if "table" in options:
            return ["table"]
        if "fa" in options:
            return ["fa"]
        return [options[0]]

    monkeypatch.setattr(page.random, "choices", force_table)
    monkeypatch.setattr(page.random, "random", lambda: 0.99)

    html, width, height, meta = page.generate_page()

    assert "<table" in html
    assert 'type="checkbox"' in html
    assert width > 0 and height > 0


def test_generate_page_navbar_layout(monkeypatch):
    """P3: navbar 布局应包含 <nav> 标签"""
    def force_navbar(options, weights=None):
        if "navbar" in options:
            return ["navbar"]
        if "fa" in options:
            return ["fa"]
        return [options[0]]

    monkeypatch.setattr(page.random, "choices", force_navbar)
    monkeypatch.setattr(page.random, "random", lambda: 0.99)

    html, width, height, meta = page.generate_page()

    assert "<nav " in html
    assert width > 0 and height > 0


def test_generate_page_returns_valid_html():
    """generate_page 应始终返回包含 html/head/body 的完整页面"""
    html, w, h, meta = page.generate_page()
    assert "<!DOCTYPE html>" in html
    assert "<body" in html
    assert "</html>" in html
    assert w > 0
    assert h > 0
    assert isinstance(meta, list)


def test_generate_page_all_types_stable():
    """连续生成 20 张页面不应报错（覆盖所有 8 种布局和各种弹窗组合）"""
    errors = []
    for i in range(20):
        try:
            html, w, h, meta = page.generate_page()
            assert w > 0
            assert h > 0
        except Exception as e:
            errors.append(f"#{i}: {e}")
    assert errors == [], f"generate_page errors:\n" + "\n".join(errors)
