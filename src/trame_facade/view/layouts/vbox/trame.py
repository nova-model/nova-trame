"""Trame implementation of the VBoxLayout class."""

from typing import Union

from trame_client.widgets.core import AbstractElement


class VBoxLayout(AbstractElement):
    """Creates an element that horizontally stacks its children."""

    def __init__(self, align: str = "start", height: Union[int, str] = "100%", width: Union[int, str] = "100%") -> None:
        """Constructor for VBoxLayout.

        Parameters
        ----------
        align : str
            The horizontal alignment of the children in the VBoxLayout. Options are :code:`start`, :code:`center`, and
            :code:`end`.
        height : int | str
            The height of this box. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.
        width : int | str
            The width of this box. If an integer is provided, it is interpreted as pixels. If a string is provided,
            the string is treated as a CSS value.

        Returns
        -------
        None

        Example
        -------
        .. code-block:: python

            from trame_facade.view.layouts.vbox import VBoxLayout


            vbox = VBoxLayout()
        """
        pass

    def add_child(self, child: AbstractElement) -> None:
        """Add a child element to the VBoxLayout.

        Parameters
        ----------
        child : AbstractElement
            The child element to add to the VBoxLayout.

        Returns
        -------
        None

        Example
        -------
        .. code-block:: python

            from trame.widgets import vuetify3 as vuetify
            from trame_facade.view.layouts.hbox import VBoxLayout


            vbox = VBoxLayout(align="center")
            vbox.add_child(vuetify.VBtn("Button 1"))
            vbox.add_child(vuetify.VBtn("Button 2"))
        """
        pass
