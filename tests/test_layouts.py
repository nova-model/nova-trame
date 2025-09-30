"""Unit tests for GridLayout, HBoxLayout, and VBoxLayout."""

from trame.widgets import html
from trame.widgets import vuetify3 as vuetify

from nova.trame.view.layouts import GridLayout, HBoxLayout, VBoxLayout


def test_grid() -> None:
    with GridLayout(columns=3, stretch=True):
        html.Div("Test 1")
        html.Div("Test 2", row_span=2, column_span=2)


def test_complex_layout() -> None:
    # [ setup complex layout example ]
    class LMRLayout:
        def __init__(self) -> None:
            with GridLayout(rows=1, columns=10, halign="center", valign="center"):
                self.left = html.Div(column_span=2)  # 20% width
                self.middle = html.Div(column_span=5)  # 50% width
                self.right = html.Div(column_span=3)  # 30% width

    my_layout = LMRLayout()
    with my_layout.left:
        vuetify.VBtn("Left Button")
    # [ setup complex layout example complete ]


def test_hbox() -> None:
    with HBoxLayout(stretch=True):
        html.Div("Test 1")
        html.Div("Test 2")


def test_vbox() -> None:
    with VBoxLayout(stretch=True):
        html.Div("Test 1")
        html.Div("Test 2")


def test_style_attributes() -> None:
    # Test dict-typed style
    with GridLayout(style={"height": "40px"}):
        html.Div("Test", style={"height": "100%"})
    with HBoxLayout(style={"height": "40px"}):
        html.Div("Test", style={"height": "100%"})
    with VBoxLayout(style={"height": "40px"}):
        html.Div("Test", style={"height": "100%"})

    # Test string-typed style
    with GridLayout(style="height: 40px"):
        html.Div("Test", style="height: 40px")
    with HBoxLayout(style="height: 40px"):
        html.Div("Test", style="height: 40px")
    with VBoxLayout(style="height: 40px"):
        html.Div("Test", style="height: 40px")
