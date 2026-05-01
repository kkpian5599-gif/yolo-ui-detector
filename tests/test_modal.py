"""Test modal, overlay, link, icon, toast, drawer generation

P1修复：generate_icon_html 现在返回 <i> 标签，meta 键为 cls/size(str)
P3新增：TestToast / TestDrawer
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.templates.modal import (
    generate_modal_html,
    generate_overlay_html,
    generate_link_html,
    generate_icon_html,
    generate_toast_html,
    generate_drawer_html,
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

    def test_modal_has_data_yolo_class(self):
        """modal 元素必须有 data-yolo-class='modal' 供 JS 选择器识别"""
        html, _ = generate_modal_html()
        assert 'data-yolo-class="modal"' in html


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

    def test_overlay_has_data_yolo_class(self):
        html, _ = generate_overlay_html()
        assert 'data-yolo-class="modal"' in html


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
    """P1修复：generate_icon_html 现在返回 <i> 标签，meta 有 cls(str) 和 size(str)"""

    def test_generate_icon_uses_i_tag(self):
        html, meta = generate_icon_html()
        assert "<i " in html, "icon should use <i> tag (Font Awesome)"
        assert meta["type"] == "icon"

    def test_icon_meta_has_cls(self):
        """meta 应包含 cls 字段（FA class 名）"""
        _, meta = generate_icon_html()
        assert "cls" in meta
        assert "fa-" in meta["cls"]

    def test_icon_meta_has_size_str(self):
        """size 是 '16px'/'24px' 这样的字符串"""
        _, meta = generate_icon_html()
        assert "size" in meta
        assert meta["size"].endswith("px")

    def test_icon_sizes_vary(self):
        sizes = set()
        for _ in range(20):
            _, meta = generate_icon_html()
            sizes.add(meta["size"])
        assert len(sizes) >= 2

    def test_icons_cls_vary(self):
        clses = set()
        for _ in range(30):
            _, meta = generate_icon_html()
            clses.add(meta["cls"])
        assert len(clses) >= 3


# ─── P3: Toast 测试 ─────────────────────────────────────
class TestToast:
    def test_toast_has_fixed_position(self):
        html, meta = generate_toast_html()
        assert "position:fixed" in html
        assert meta["type"] == "toast"

    def test_toast_variants(self):
        variants = set()
        for _ in range(40):
            _, meta = generate_toast_html()
            variants.add(meta["variant"])
        assert "success" in variants
        assert "error" in variants

    def test_toast_positions_vary(self):
        positions = set()
        for _ in range(40):
            _, meta = generate_toast_html()
            positions.add(meta["position"])
        assert len(positions) >= 2

    def test_toast_has_yolo_class(self):
        html, _ = generate_toast_html()
        assert 'data-yolo-class="modal"' in html

    def test_toast_has_message_text(self):
        """toast 应包含可辨识的通知文字"""
        found = False
        for _ in range(10):
            html, _ = generate_toast_html()
            if any(msg in html for msg in ["成功", "失败", "Success", "Error", "Warning", "Info"]):
                found = True
                break
        assert found


# ─── P3: Drawer 测试 ────────────────────────────────────
class TestDrawer:
    def test_drawer_has_overlay(self):
        html, meta = generate_drawer_html()
        assert "drawer-overlay" in html
        assert meta["type"] == "drawer"

    def test_drawer_has_panel(self):
        html, _ = generate_drawer_html()
        assert "drawer-panel" in html

    def test_drawer_has_yolo_class(self):
        html, _ = generate_drawer_html()
        assert 'data-yolo-class="modal"' in html

    def test_drawer_has_footer_buttons(self):
        """抽屉底部应有取消按钮"""
        found = False
        for _ in range(10):
            html, _ = generate_drawer_html()
            if any(txt in html for txt in ["取消", "关闭", "Cancel"]):
                found = True
                break
        assert found

    def test_drawer_width_in_meta(self):
        _, meta = generate_drawer_html()
        assert "width" in meta
        assert meta["width"] in (320, 360, 400, 440)

    def test_drawer_dark_variant(self):
        dark_seen = False
        for _ in range(30):
            _, meta = generate_drawer_html()
            if meta["dark"]:
                dark_seen = True
                break
        assert dark_seen
