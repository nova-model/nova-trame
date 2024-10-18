"""Trame implementation of the VBoxLayout class."""

from typing import Any, Union

from trame.widgets import html


class VBoxLayout(html.Div):
    """Creates an element that vertically stacks its children."""

    def __init__(
        self, height: Union[int, str] = "100%", width: Union[int, str] = "100%", align: str = "start", **kwargs: Any
    ) -> None:
        """Constructor for VBoxLayout.

        Parameters
        ----------
        height : int | str
            The height of this box. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.
        width : int | str
            The width of this box. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.
        align : str
            The horizontal alignment of the children in the VBoxLayout. Options are :code:`start`, :code:`center`, and
            :code:`end`.
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
        classes += " d-box flex-column"

        style = self.get_root_styles(height, width, align) | kwargs.pop("style", {})

        super().__init__(classes=classes, style=style, **kwargs)

    def get_root_styles(self, height: Union[int, str], width: Union[int, str], align: str) -> dict:
        height = f"{height}px" if isinstance(height, int) else height
        width = f"{width}px" if isinstance(width, int) else width

        styles = {
            "height": height,
            "width": width,
        }

        if align:
            styles["align-items"] = align

        return styles
