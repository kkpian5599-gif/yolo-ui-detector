"""Test config: style_profile loading, constants, class mapping"""
import pytest
import sys
from pathlib import Path

# Ensure generator is importable
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfig:
    def test_classes_count(self):
        """9 classes: button, input, checkbox, radio, select, textarea, link, icon, modal"""
        from generator.config import CLASSES, NUM_CLASSES

        assert len(CLASSES) == 9
        assert NUM_CLASSES == 9
        assert CLASSES[0] == "button"
        assert CLASSES[8] == "modal"

    def test_class2id_mapping(self):
        from generator.config import CLASS2ID

        assert CLASS2ID["button"] == 0
        assert CLASS2ID["modal"] == 8
        assert CLASS2ID["icon"] == 7

    def test_constants_present(self):
        from generator.config import BTN_TEXTS, INPUT_PLACEHOLDERS, LINK_TEXTS

        assert len(BTN_TEXTS) > 10
        assert len(INPUT_PLACEHOLDERS) > 5
        assert len(LINK_TEXTS) > 5
        assert "确定" in BTN_TEXTS
        assert "请输入" in INPUT_PLACEHOLDERS

    def test_page_sizes(self):
        from generator.config import PAGE_SIZES

        assert len(PAGE_SIZES) == 4
        assert (1920, 1080) in PAGE_SIZES

    def test_dark_theme_loaded(self):
        from generator.config import DARK

        assert "bg_page" in DARK
        assert len(DARK["bg_page"]) >= 2
        assert "text_primary" in DARK

    def test_style_profile_loaded(self):
        from generator.config import STYLE_PROFILE

        assert "buttons" in STYLE_PROFILE
        assert "inputs" in STYLE_PROFILE
        assert "dark_theme" in STYLE_PROFILE
        assert "modals_and_overlays" in STYLE_PROFILE
        assert "_meta" in STYLE_PROFILE

    def test_config_missing_file_handled(self, monkeypatch):
        """If profile doesn't exist, should exit with error"""
        import generator.config as cfg

        # Simulate missing file
        def mock_read(*args, **kwargs):
            raise FileNotFoundError("no file")

        monkeypatch.setattr(Path, "read_text", mock_read)
        monkeypatch.setattr(cfg, "PROFILE_PATH", Path("/nonexistent/profile.json"))

        with pytest.raises(SystemExit) as exc:
            # Re-trigger the import-time logic
            import importlib
            importlib.reload(cfg)
        assert exc.value.code == 1
