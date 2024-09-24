"""Unit tests for EasyGrid."""

from trame.ui.vuetify3 import VAppLayout
from trame.widgets import html
from trame_server.core import Server

from trame_facade.components.easy_grid import EasyGrid


def test_easy_grid() -> None:
    """Test the EasyGrid class."""
    server = Server()
    with VAppLayout(server):
        grid = EasyGrid()
        assert grid.cols_per_row == 1
        assert grid.dense is False
        assert grid.skip_child is False


def test_invalid_easy_grid() -> None:
    server = Server()
    with VAppLayout(server):
        try:
            EasyGrid(cols_per_row=0)
            raise AssertionError("Expected ValueError for cols_per_row < 1")
        except ValueError:
            pass


def test_add_child() -> None:
    server = Server()
    with VAppLayout(server):
        grid = EasyGrid(dense=True)
        grid.add_child(html.Div())


def test_add_children() -> None:
    server = Server()
    with VAppLayout(server):
        grid = EasyGrid(dense=True)
        grid.add_children([html.Div(), html.Div()])
