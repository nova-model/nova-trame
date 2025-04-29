"""Unit tests for DataSelector."""

from warnings import catch_warnings

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
                    input = DataSelector(v_model="test")
                    assert input.v_model == "test"
                    assert input._model.state.facility == ""
                    assert input._model.state.instrument == ""
                    assert input._model.state.experiment == ""

                    input.set_state(facility="HFIR", instrument="CG-2", experiment="IPTS-27744")
                    assert input._model.state.facility == "HFIR"
                    assert input._model.state.instrument == "CG-2"
                    assert input._model.state.experiment == "IPTS-27744"

                    with catch_warnings(record=True) as captured_warnings:
                        input.set_state(facility="NSS")
                        assert str(captured_warnings[0].message).startswith("Facility 'NSS' could not be found.")

                    with catch_warnings(record=True) as captured_warnings:
                        DataSelector(v_model="test", facility="HIFR")
                        assert str(captured_warnings[0].message).startswith("Facility 'HIFR' could not be found.")

                    with catch_warnings(record=True) as captured_warnings:
                        DataSelector(v_model="test", facility="SNS", instrument="BL1B")
                        assert str(captured_warnings[0].message).startswith(
                            "Instrument 'BL1B' could not be found in 'SNS'."
                        )

    MyTrameApp()
