"""Unit tests for GridLayout, HBoxLayout, and VBoxLayout."""

from trame.widgets import vuetify3 as vuetify

from trame_facade.view.layouts import GridLayout, HBoxLayout, VBoxLayout


def test_grid() -> None:
    # [ setup GridLayout.add_child example ]
    grid = GridLayout(rows=2, columns=3)
    grid.add_child("Test 1", row=0, column=0)
    grid.add_child("Test 2", row=0, column=1, row_span=2, column_span=2)
    # [ setup GridLayout.add_child example complete ]

    try:
        grid.add_child("Test 3", row_span=2)
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass

    try:
        grid.add_child("Test 3", column_span=2)
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass

    try:
        grid.add_child("Test 3", row=1)
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass

    try:
        grid.add_child("Test 3", column=1)
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass


def test_complex_layout() -> None:
    # [ setup complex layout example ]
    class LMRLayout:
        def __init__(self) -> None:
            self.grid = GridLayout(rows=1, columns=10, halign="center", valign="center")

            self.left = self.grid.add_child("Left Column", row=0, column=0, column_span=2)  # 20% width
            self.middle = self.grid.add_child("Middle Column", row=0, column=2, column_span=5)  # 50% width
            self.right = self.grid.add_child("Right Column", row=0, column=7, column_span=3)  # 30% width

    my_layout = LMRLayout()
    my_layout.left = vuetify.VBtn("Left Button")
    my_layout.middle = vuetify.VBtn("Middle Button")
    my_layout.right = vuetify.VBtn("Right Button")
    # [ setup complex layout example complete ]


def test_hbox() -> None:
    hbox = HBoxLayout()
    hbox.add_child("Test 1")
    hbox.add_child("Test 2")


def test_vbox() -> None:
    vbox = VBoxLayout()
    vbox.add_child("Test 1")
    vbox.add_child("Test 2")
