"""Trame implementation of the GridLayout class."""

from typing import Any, Optional, Union

from trame.widgets import html
from trame_client.widgets.core import AbstractElement


class GridLayout(html.Div):
    """Creates a grid with a specified number of rows and columns."""

    def __init__(
        self,
        rows: int = 1,
        columns: int = 1,
        height: Union[int, str] = "100%",
        width: Union[int, str] = "100%",
        halign: Optional[str] = None,
        valign: Optional[str] = None,
        **kwargs: Any,
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
        halign : optional[str]
            The horizontal alignment of items in the grid. Options are :code:`start`, :code:`center`, and :code:`end`.
        valign : optional[str]
            The vertical alignment of items in the grid. Options are :code:`start`, :code:`center`, and :code:`end`.
        kwargs : Any
            Additional keyword arguments to pass to html.Div.

        Returns
        -------
        None

        Examples
        --------
        Basic usage:

        .. literalinclude:: ../tests/gallery/app.py
            :start-after: setup grid
            :end-before: setup grid complete
            :dedent:

        Building a custom left-middle-right layout:

        .. literalinclude:: ../tests/test_layouts.py
            :start-after: setup complex layout example
            :end-before: setup complex layout example complete
            :dedent:
        """
        classes = kwargs.pop("classes", [])
        if isinstance(classes, list):
            classes = " ".join(classes)
        classes += " d-grid"

        style = self.get_root_styles(rows, columns, height, width, halign, valign) | kwargs.pop("style", {})

        super().__init__(classes=classes, style=style, **kwargs)

    def get_root_styles(
        self,
        rows: int,
        columns: int,
        height: Union[int, str],
        width: Union[int, str],
        halign: Optional[str],
        valign: Optional[str],
    ) -> dict[str, str]:
        height = f"{height}px" if isinstance(height, int) else height
        width = f"{width}px" if isinstance(width, int) else width

        styles = {
            "grid-template-rows": f"repeat({rows}, 1fr)",
            "grid-template-columns": f"repeat({columns}, 1fr)",
            "height": height,
            "width": width,
        }

        if halign:
            styles["justify-items"] = halign

        if valign:
            styles["align-items"] = valign

        return styles

    def get_row_style(self, row: int, row_span: int) -> str:
        if row >= 0:
            return f"grid-row: {row + 1} / span {row_span};"
        return ""

    def get_column_style(self, column: int, column_span: int) -> str:
        if column >= 0:
            return f"grid-column: {column + 1} / span {column_span};"
        return ""

    def validate_position(self, row: int, column: int, row_span: int, column_span: int) -> None:
        if row < 0 and row_span > 1:
            raise ValueError("You must set row explicitly in order to set row_span.")
        if column < 0 and column_span > 1:
            raise ValueError("You must set column explicitly in order to set column_span.")
        if row < 0 and column >= 0:
            raise ValueError("You must set row explicitly in order to set column explicitly.")
        if column < 0 and row >= 0:
            raise ValueError("You must set column explicitly in order to set row explicitly.")

    def add_child(
        self,
        child: Union[AbstractElement, str],
        row: int = -1,
        column: int = -1,
        row_span: int = 1,
        column_span: int = 1,
    ) -> AbstractElement:
        """Add a child element to the grid.

        Parameters
        ----------
        child : `AbstractElement <https://trame.readthedocs.io/en/latest/core.widget.html#trame_client.widgets.core.AbstractElement>`_
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
            The child element that was added to the grid.

        Example
        -------
        .. literalinclude:: ../tests/test_layouts.py
            :start-after: setup GridLayout.add_child example
            :end-before: setup GridLayout.add_child example complete
            :dedent:
        """
        self.validate_position(row, column, row_span, column_span)

        if isinstance(child, str):
            child = html.Div(child)

        child.style = f"{self.get_row_style(row, row_span)} {self.get_column_style(column, column_span)}"

        super().add_child(child)

        return child
