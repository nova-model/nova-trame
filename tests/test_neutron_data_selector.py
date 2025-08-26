"""Unit tests for NeutronDataSelector."""

from typing import List
from warnings import catch_warnings

from pydantic import BaseModel, Field
from trame.app import get_server
from trame_server.core import Server

from nova.mvvm.trame_binding import TrameBinding
from nova.trame.view.components.ornl import NeutronDataSelector
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
                    input = NeutronDataSelector(v_model="test", extensions=[".tiff"])
                    assert input.v_model == "test"
                    assert input._extensions == [".tiff"]
                    assert input._model.state.facility == ""
                    assert input._model.state.instrument == ""
                    assert input._model.state.experiment == ""

                    input.update_facility("HFIR")
                    input.update_instrument("BIO-SANS")
                    input.update_experiment("IPTS-24666")

                    with catch_warnings(record=True) as captured_warnings:
                        input.update_facility(facility="NSS")
                        assert str(captured_warnings[0].message).startswith("Facility 'NSS' could not be found.")

                    with catch_warnings(record=True) as captured_warnings:
                        NeutronDataSelector(v_model="test", facility="HIFR")
                        assert str(captured_warnings[0].message).startswith("Facility 'HIFR' could not be found.")

                    with catch_warnings(record=True) as captured_warnings:
                        NeutronDataSelector(v_model="test", facility="SNS", instrument="BL1B")
                        assert str(captured_warnings[0].message).startswith(
                            "Instrument 'BL1B' could not be found in 'SNS'."
                        )

                    try:
                        input.set_state()
                        raise AssertionError("set_state should fail to run")
                    except TypeError:
                        pass

    MyTrameApp()


def test_parameter_bindings() -> None:
    class TestModel(BaseModel):
        v_model: List[str] = Field(default=[])
        facility: str = Field(default="")
        instrument: str = Field(default="")
        experiment: str = Field(default="")
        allow_custom_directories: bool = Field(default=False)

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
            self.test_binding.connect("test_nds")

        def create_ui(self) -> None:
            with super().create_ui() as layout:
                with layout.content:
                    NeutronDataSelector(
                        v_model=("test_nds.v_model", ["test.txt"]),
                        facility=("test_nds.facility", "SNS"),
                        instrument=("test_nds.instrument", "TOPAZ"),
                        experiment=("test_nds.experiment",),
                        allow_custom_directories=("test_nds.allow_custom_directories", True),
                    )

    MyTrameApp()
