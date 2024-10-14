"""Trame implementation of the GridLayout class."""

from typing import Union

from trame_client.widgets.core import AbstractElement


class GridLayout(AbstractElement):
    """Creates a grid with a specified number of rows and columns."""

    def __init__(
        self,
        rows: int = 1,
        columns: int = 1,
        height: Union[int, str] = "100%",
        width: Union[int, str] = "100%",
        halign: str = "start",
        valign: str = "start",
    ) -> None:
        """Constructor for GridLayout.

        Parameters
        ----------
        rows : int
            The number of rows in the grid.
        columns : int
            The number of columns in the grid.
        height : int | str
            The height of this grid. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.
        width : int | str
            The width of this grid. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.
        halign : str
            The horizontal alignment of items in the grid. Options are :code:`start`, :code:`center`, and :code:`end`.
        valign : str
            The vertical alignment of items in the grid. Options are :code:`start`, :code:`center`, and :code:`end`.

        Returns
        -------
        None

        Examples
        --------
        Basic usage (400px by 400px grid with 3 rows and 3 columns):

        .. code-block:: python

            from trame_facade.view.layouts.grid import GridLayout


            grid = GridLayout(rows=3, columns=3, height=400, width=400)

        Building a custom left-middle-right layout:

        .. code-block:: python

            from trame_facade.view.layouts.grid import GridLayout


            class LMRLayout:
                def __init__(self):
                    self.grid = GridLayout(rows=1, columns=10, halign="center", valign="center")
                    self.left = self.grid.add_child("Left Column", column=0, column_span=2)  # 20% width
                    self.middle = self.grid.add_child("Middle Column", column=2, column_span=5)  # 50% width
                    self.right = self.grid.add_child("Right Column", column=7, column_span=3)  # 30% width


            my_layout = LMRLayout()
            my_layout.left = vuetify.VBtn("Left Button")
            my_layout.middle = vuetify.VBtn("Middle Button")
            my_layout.right = vuetify.VBtn("Right Button")


        """
        pass

    def add_child(
        self, child: AbstractElement, row: int = 0, column: int = 0, row_span: int = 1, column_span: int = 1
    ) -> AbstractElement:
        """Add a child element to the grid.

        Parameters
        ----------
        child : AbstractElement
            The child element to add to the grid.
        row : int
            The row index to place the child in.
        column : int
            The column index to place the child in.
        row_span : int
            The number of rows the child should span.
        column_span : int
            The number of columns the child should span.

        Returns
        -------
        `AbstractElement <https://trame.readthedocs.io/en/latest/core.widget.html#trame_client.widgets.core.AbstractElement>`_

        Example
        -------
        .. code-block:: python

            from trame.widgets import vuetify3 as vuetify
            from trame_facade.view.layouts.grid import GridLayout


            grid = GridLayout(rows=2, columns=3)
            child1 = vuetify.VBtn("Button 1")
            child2 = vuetify.VBtn("Button 2")
            grid.add_child(child, row=0, column=0)
            grid.add_child(child, row=1, column=1, row_span=2, column_span=2)
        """
        pass
