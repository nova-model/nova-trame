"""Tests theme.py."""

from nova.trame import ThemedApp


def test_theme_configuration() -> None:
    app = ThemedApp(vuetify_config_overrides={"primary": "#ff0000"})
    assert app.vuetify_config["theme"]["themes"]["ModernTheme"]["colors"]["primary"] == "#ff0000"


def test_set_theme() -> None:
    app = ThemedApp()
    assert app.state.nova__theme == "ModernTheme"
    app.set_theme("CompactTheme", force=True)
    assert app.state.nova__theme == "CompactTheme"
    try:
        app.set_theme("FakeTheme")
        raise AssertionError("Expected ValueError")
    except ValueError as e:
        assert str(e).startswith("Theme 'FakeTheme' not found")


def test_inheritance() -> None:
    # [setup app]
    from trame.widgets import vuetify3 as vuetify
    from trame_server.core import Server

    class MyTrameApp(ThemedApp):
        def __init__(self, server: Server = None) -> None:
            super().__init__(server=server)

            self.create_ui()

        def create_ui(self) -> None:
            with super().create_ui() as layout:
                with layout.content:
                    vuetify.VBtn("Hello World")

    # [setup app complete]
