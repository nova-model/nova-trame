"""Trame implementation of the VBoxLayout class."""

from typing import Any, Optional, Union

from trame.widgets import html


class VBoxLayout(html.Div):
    """Creates an element that vertically stacks its children."""

    def __init__(
        self,
        height: Optional[Union[int, str]] = None,
        width: Optional[Union[int, str]] = None,
        halign: Optional[str] = None,
        valign: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Constructor for VBoxLayout.

        Parameters
        ----------
        height : optional[int | str]
            The height of this box. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.
        width : optional[int | str]
            The width of this box. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.
        halign : optional[str]
            The horizontal alignment of items in the grid. See `MDN
            <https://developer.mozilla.org/en-US/docs/Web/CSS/align-items>`__ for available options.
        valign : optional[str]
            The vertical alignment of items in the grid. See `MDN
            <https://developer.mozilla.org/en-US/docs/Web/CSS/justify-items>`__ for available options.
        kwargs : Any
            Additional keyword arguments to pass to html.Div.

        Returns
        -------
        None

        Example
        -------
        .. literalinclude:: ../tests/gallery/app.py
            :start-after: setup vbox
            :end-before: setup vbox complete
            :dedent:
        """
        classes = kwargs.pop("classes", [])
        if isinstance(classes, list):
            classes = " ".join(classes)
        classes += " d-flex flex-column"

        style = self.get_root_styles(height, width, halign, valign) | kwargs.pop("style", {})

        super().__init__(classes=classes, style=style, **kwargs)

    def get_root_styles(
        self,
        height: Optional[Union[int, str]],
        width: Optional[Union[int, str]],
        halign: Optional[str],
        valign: Optional[str],
    ) -> dict:
        height = f"{height}px" if isinstance(height, int) else height
        width = f"{width}px" if isinstance(width, int) else width

        styles = {}

        if height:
            styles["height"] = height
        if width:
            styles["width"] = width
        if halign:
            styles["align-items"] = halign
        if valign:
            styles["justify-content"] = valign

        return styles
