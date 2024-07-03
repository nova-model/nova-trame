from trame.widgets import vuetify3 as vuetify


VUETIFY_COLS = 12  # Max number of columns in a Vuetify grid


class EasyGrid(vuetify.VContainer):
    """Helper class for generating vuetify3.VContainer objects."""

    def __init__(self, cols_per_row: int = 1, **kwargs):
        if (
            not isinstance(cols_per_row, int)
            or cols_per_row < 1
            or cols_per_row > VUETIFY_COLS
        ):
            raise ValueError(
                f"cols_per_row must be a positive integer between 1 and {VUETIFY_COLS}"
            )

        super().__init__(**kwargs)
        self._attr_names += ["cols_per_row"]

        self.cols_per_row = cols_per_row
        self.skip_child = False
        self.last_row = None
        self.last_row_slots = 0

    def add_child(self, child):
        if self.skip_child:
            self.skip_child = False
            return

        if self.last_row is None or self.last_row_slots == 0:
            """Calling vuetify.VRow() (or any component) will trigger a recursive call to self.add_child.
            In those calls, we don't actually want to do anything since we're going to add to the element stack manually,
            so we set a class attribute that informs us to skip the next child."""
            self.skip_child = True
            self.last_row = vuetify.VRow()
            self.last_row_slots = self.cols_per_row

            super().add_child(self.last_row)

        # Again, we need to skip the next child since we're going to add it manually
        self.skip_child = True
        col = vuetify.VCol(cols="12", lg=VUETIFY_COLS // self.cols_per_row)
        col.add_child(child)

        self.last_row.add_child(col)
        self.last_row_slots -= 1

    def add_children(self, children):
        for child in children:
            self.add_child(child)
