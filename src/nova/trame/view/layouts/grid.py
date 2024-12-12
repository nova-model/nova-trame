"""Trame implementation of the GridLayout class."""

from typing import Any, Optional, Union

from trame.widgets import html
from trame_client.widgets.core import AbstractElement


class GridLayout(html.Div):
    """Creates a grid with a specified number of columns."""

    def __init__(
        self,
        columns: int = 1,
        height: Optional[Union[int, str]] = None,
        width: Optional[Union[int, str]] = None,
        halign: Optional[str] = None,
        valign: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Constructor for GridLayout.

        Parameters
        ----------
        columns : int
            The number of columns in the grid.
        height : optional[int | str]
            The height of this grid. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.
        width : optional[int | str]
            The width of this grid. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.
        halign : optional[str]
            The horizontal alignment of items in the grid. See `MDN
            <https://developer.mozilla.org/en-US/docs/Web/CSS/justify-items>`__ for available options.
        valign : optional[str]
            The vertical alignment of items in the grid. See `MDN
            <https://developer.mozilla.org/en-US/docs/Web/CSS/align-items>`__ for available options.
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

        style = self.get_root_styles(columns, height, width, halign, valign) | kwargs.pop("style", {})

        super().__init__(classes=classes, style=style, **kwargs)

    def get_root_styles(
        self,
        columns: int,
        height: Optional[Union[int, str]],
        width: Optional[Union[int, str]],
        halign: Optional[str],
        valign: Optional[str],
    ) -> dict[str, str]:
        height = f"{height}px" if isinstance(height, int) else height
        width = f"{width}px" if isinstance(width, int) else width

        styles = {
            "grid-template-columns": f"repeat({columns}, 1fr)",
        }

        if height:
            styles["height"] = height
        if width:
            styles["width"] = width
        if halign:
            styles["justify-items"] = halign
        if valign:
            styles["align-items"] = valign

        return styles

    def get_row_style(self, row_span: int) -> str:
        return f"grid-row-end: span {row_span};"

    def get_column_style(self, column_span: int) -> str:
        return f"grid-column-end: span {column_span};"

    def add_child(self, child: Union[AbstractElement, str]) -> AbstractElement:
        """Add a child to the grid.

        Do not call this directly. Instead, use Trame's `with` syntax, which will call this method internally. This
        method is documented here as a reference for the span parameters.

        Parameters
        ----------
        child : `AbstractElement \
            <https://trame.readthedocs.io/en/latest/core.widget.html#trame_client.widgets.core.AbstractElement>`_ | str
            The child to add to the grid.
        row_span : int
            The number of rows this child should span.
        column_span : int
            The number of columns this child should span.

        Returns
        -------
        None

        Example
        -------
        .. literalinclude:: ../tests/gallery/app.py
            :start-after: grid row and column span example
            :end-before: grid row and column span example end
            :dedent:
        """
        if isinstance(child, str):
            child = html.Div(child)

        row_span = 1
        column_span = 1
        if "row_span" in child._py_attr:
            row_span = child._py_attr["row_span"]
        if "column_span" in child._py_attr:
            column_span = child._py_attr["column_span"]

        if "style" not in child._py_attr or child.style is None:
            child.style = ""
        child.style += f"; {self.get_row_style(row_span)} {self.get_column_style(column_span)}"

        if "classes" not in child._py_attr or child.classes is None:
            child.classes = ""
        child.classes += " d-grid-item"

        super().add_child(child)
