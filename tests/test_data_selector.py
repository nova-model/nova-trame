"""Unit tests for DataSelector."""

from pydantic import ValidationError
from trame.app import get_server
from trame_server.core import Server

from nova.trame.view.components import DataSelector
from nova.trame.view.theme import ThemedApp


def test_data_selector() -> None:
    class MyTrameApp(ThemedApp):
        def __init__(self, server: Server = None) -> None:
            server = get_server(None, client_type="vue3")
            super().__init__(server=server)
            self.create_ui()

        def create_ui(self) -> None:
            with super().create_ui() as layout:
                with layout.content:
                    input = DataSelector()
                    assert input._model.state.facility == ""
                    assert input._model.state.instrument == ""
                    assert input._model.state.experiment == ""

                    input.set_state(facility="HFIR", instrument="CG2", experiment="IPTS-27744")
                    assert input._model.state.facility == "HFIR"
                    assert input._model.state.instrument == "CG2"
                    assert input._model.state.experiment == "IPTS-27744"

                    try:
                        input.set_state(facility="NSS")
                        raise AssertionError("Invalid facility should trigger a ValidationError")
                    except ValidationError:
                        pass

    MyTrameApp()
