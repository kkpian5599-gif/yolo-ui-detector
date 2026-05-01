"""Test renderer: map_to_class function"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.renderer import map_to_class


class TestMapToClass:
    def test_button_maps_to_0(self):
        assert map_to_class("button", "", "", "确定") == 0

    def test_text_input_maps_to_1(self):
        assert map_to_class("input", "text", "", "") == 1

    def test_password_input_maps_to_1(self):
        assert map_to_class("input", "password", "", "") == 1

    def test_checkbox_maps_to_2(self):
        assert map_to_class("input", "checkbox", "", "") == 2

    def test_radio_maps_to_3(self):
        assert map_to_class("input", "radio", "", "") == 3

    def test_select_maps_to_4(self):
        assert map_to_class("select", "", "", "") == 4

    def test_textarea_maps_to_5(self):
        assert map_to_class("textarea", "", "", "") == 5

    def test_link_maps_to_6(self):
        assert map_to_class("a", "", "", "了解更多") == 6

    def test_icon_maps_to_7(self):
        # P1修复：icon 现在用 <i> 标签（Font Awesome）不是 span+emoji
        assert map_to_class("i", "", "fa-solid fa-search", "") == 7

    def test_modal_overlay_maps_to_8(self):
        assert map_to_class("div", "", "modal-overlay", "") == 8

    def test_overlay_area_maps_to_8(self):
        assert map_to_class("div", "", "overlay-area", "") == 8

    def test_label_checkbox_maps_to_2(self):
        assert map_to_class("label", "", "checkbox-wrapper", "") == 2

    def test_label_radio_maps_to_3(self):
        assert map_to_class("label", "", "radio-group", "") == 3

    def test_unknown_tag_returns_negative(self):
        result = map_to_class("div", "", "", "hello")
        assert result < 0

    def test_unknown_input_type_returns_1(self):
        """Input without checkbox/radio type defaults to 1"""
        assert map_to_class("input", "email", "", "") == 1

    def test_empty_strings_dont_crash(self):
        result = map_to_class("", "", "", "")
        assert result < 0
