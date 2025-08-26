"""Unit tests for DataSelector."""

from typing import List

from pydantic import BaseModel, Field
from trame.app import get_server
from trame_server.core import Server

from nova.mvvm.trame_binding import TrameBinding
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
                    input = DataSelector(v_model="test", directory="/", extensions=[".tiff"])
                    assert input.v_model == "test"
                    assert input._directory == "/"
                    assert input._extensions == [".tiff"]

    MyTrameApp()


def test_parameter_bindings() -> None:
    class TestModel(BaseModel):
        v_model: List[str] = Field(default=[])
        directory: str = Field(default="")
        extensions: List[str] = Field(default=[])
        refresh_rate: int = Field(default=0)
        select_strategy: str = Field(default="")
        subdirectory: str = Field(default="")

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
            self.test_binding.connect("test_ds")

        def create_ui(self) -> None:
            with super().create_ui() as layout:
                with layout.content:
                    DataSelector(
                        v_model=("test_ds.v_model", ["test.txt"]),
                        directory=("test_ds.directory", "/"),
                        extensions=("test_ds.extensions", [".txt"]),
                        subdirectory=("test_ds.subdirectory", "bin"),
                        refresh_rate=("test_ds.refresh_rate", 15),
                        select_strategy=("test_ds.select_strategy", "page"),
                    )

    MyTrameApp()
