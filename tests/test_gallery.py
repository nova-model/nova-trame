"""Tries to create an instance of the gallery's App class."""

from tests.gallery import App


def test_gallery() -> None:
    app = App()
    assert app.state.trame__title == "Widget Gallery"
