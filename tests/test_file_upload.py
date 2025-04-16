"""Unit tests for FileUpload."""

from trame.app import get_server
from trame_server.core import Server

from nova.trame.view.components import FileUpload
from nova.trame.view.theme import ThemedApp


def test_file_upload() -> None:
    class MyTrameApp(ThemedApp):
        def __init__(self, server: Server = None) -> None:
            server = get_server(None, client_type="vue3")
            super().__init__(server=server)
            self.create_ui()

        def create_ui(self) -> None:
            with super().create_ui() as layout:
                with layout.content:
                    file_upload = FileUpload(v_model="test", base_paths=["/HFIR", "/SNS"], label="Test Upload")
                    assert file_upload.remote_file_input.v_model == "test"
                    assert file_upload.remote_file_input.base_paths == ["/HFIR", "/SNS"]
                    assert file_upload.children[0] == "Test Upload"

    MyTrameApp()
