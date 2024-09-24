"""Tests theme.py."""

from trame_facade import ThemedApp


def test_theme_configuration() -> None:
    app = ThemedApp(vuetify_config_overrides={"primary": "#ff0000"})
    assert app.vuetify_config["theme"]["themes"]["ModernTheme"]["colors"]["primary"] == "#ff0000"


def test_set_theme() -> None:
    app = ThemedApp()
    assert app.state.facade__theme == "ModernTheme"
    app.set_theme("TechnicalTheme", force=True)
    assert app.state.facade__theme == "TechnicalTheme"
