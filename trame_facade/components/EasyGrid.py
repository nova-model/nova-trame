from trame.widgets import vuetify3 as vuetify


VUETIFY_COLS = 12  # Max number of columns in a Vuetify grid


class EasyGrid(vuetify.VContainer):
    """Helper class for generating vuetify3.VContainer objects."""

    def __init__(self, cols_per_row: int = 1, dense: bool = False, **kwargs):
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
        self.dense = dense
        self.skip_child = False
        self.last_row = None

    def add_child(self, child):
        if self.skip_child:
            self.skip_child = False
            return

        if self.last_row is None:
            """Calling vuetify.VRow() (or any component) will trigger a recursive call to self.add_child.
            In those calls, we don't actually want to do anything since we're going to add to the element stack manually,
            so we set a class attribute that informs us to skip the next child."""
            self.skip_child = True
            self.last_row = vuetify.VRow()

            if self.dense:
                self.last_row.dense = True

            super().add_child(self.last_row)

        # Again, we need to skip the next child since we're going to add it manually
        self.skip_child = True
        col = vuetify.VCol(cols="12", lg=VUETIFY_COLS // self.cols_per_row)

        # These attributes need to exist on the column rather than the child to allow for proper rendering.
        # Vue's v_for behavior will cause every child to be rendered into a single column if this isn't done.
        for attr in ["v_for", "cols", "xs", "sm", "md", "lg", "xl", "xxl"]:
            if attr in child._py_attr:
                setattr(col, attr, child._py_attr[attr])
                setattr(child, attr, None)
        col.add_child(child)

        self.last_row.add_child(col)

    def add_children(self, children):
        for child in children:
            self.add_child(child)
