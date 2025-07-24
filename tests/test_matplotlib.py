"""Unit tests for MatplotlibFigure."""

from matplotlib.figure import Figure
from pydantic import BaseModel, Field
from trame.app import get_server
from trame_server.core import Server

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.view.components.visualization import MatplotlibFigure
from nova.trame.view.theme import ThemedApp


def test_matplotlib() -> None:
    mpl_figure = Figure()

    svg_test = MatplotlibFigure()
    assert svg_test._webagg is False

    svg_test.update(None)
    svg_test.update(mpl_figure)

    webagg_test = MatplotlibFigure(webagg=True)
    assert webagg_test._webagg is True

    webagg_test.update(None)
    webagg_test.update(mpl_figure)


def test_parameter_bindings() -> None:
    class TestModel(BaseModel):
        class Config:
            arbitrary_types_allowed = True

        figure: Figure = Field(default=Figure())

    class MyTrameApp(ThemedApp):
        def __init__(self, server: Server = None) -> None:
            self.server = get_server(None, client_type="vue3")
            super().__init__(server=self.server)

            self.create_binding()
            self.create_ui()

        def create_binding(self) -> None:
            self.test_obj = TestModel()

            binding = TrameBinding(self.server.state)
            self.test_binding = binding.new_bind(self.test_obj)
            self.test_binding.connect("test_mpl")

        def create_ui(self) -> None:
            with super().create_ui() as layout:
                with layout.content:
                    MatplotlibFigure(figure=("test_mpl.figure",))
                    MatplotlibFigure(figure=("test_mpl.figure",), webagg=True)

    MyTrameApp()
