"""View model for RemoteFileInput."""

from typing import Any, Union

from nova.mvvm.interface import BindingInterface
from nova.trame.model.remote_file_input import RemoteFileInputModel


class RemoteFileInputViewModel:
    """Manages the view state of RemoteFileInput."""

    counter = 0

    def __init__(self, model: RemoteFileInputModel, binding: BindingInterface) -> None:
        """Creates a new RemoteFileInputViewModel."""
        self.model = model

        # Needed to keep state variables separated if this class is instantiated multiple times.
        self.id = RemoteFileInputViewModel.counter
        RemoteFileInputViewModel.counter += 1

        self.showing_all_files = False
        self.showing_base_paths = True
        self.previous_value = ""
        self.value = ""
        self.dialog_bind = binding.new_bind()
        self.file_list_bind = binding.new_bind()
        self.filter_bind = binding.new_bind()
        self.showing_all_bind = binding.new_bind()
        self.valid_selection_bind = binding.new_bind()
        self.on_close_bind = binding.new_bind()
        self.on_update_bind = binding.new_bind()

    def open_dialog(self) -> None:
        self.previous_value = self.value
        self.populate_file_list()

    def close_dialog(self, cancel: bool = False) -> None:
        if not cancel:
            self.on_update_bind.update_in_view(self.value)
        else:
            self.value = self.previous_value

        self.filter_bind.update_in_view(self.value)
        self.on_close_bind.update_in_view(None)

    def filter_paths(self, filter: str) -> None:
        self.populate_file_list(filter)

    def get_dialog_state_name(self) -> str:
        return f"nova__dialog_{self.id}"

    def get_file_list_state_name(self) -> str:
        return f"nova__file_list_{self.id}"

    def get_filter_state_name(self) -> str:
        return f"nova__filter_{self.id}"

    def get_showing_all_state_name(self) -> str:
        return f"nova__showing_all_{self.id}"

    def get_valid_selection_state_name(self) -> str:
        return f"nova__valid_selection_{self.id}"

    def init_view(self) -> None:
        self.dialog_bind.update_in_view(False)
        self.valid_selection_bind.update_in_view(False)
        self.showing_all_bind.update_in_view(self.showing_all_files)

    def set_value(self, value: str) -> None:
        self.value = value

    def toggle_showing_all_files(self) -> None:
        self.showing_all_files = not self.showing_all_files
        self.showing_all_bind.update_in_view(self.showing_all_files)
        self.populate_file_list()

    def populate_file_list(self, filter: str = "") -> None:
        files = self.scan_current_path(filter)
        self.file_list_bind.update_in_view(files)

    def scan_current_path(self, filter: str) -> list[dict[str, Any]]:
        files, self.showing_base_paths = self.model.scan_current_path(self.value, self.showing_all_files, filter)

        return files

    def select_file(self, file: Union[dict[str, str], str]) -> None:
        new_path = self.model.select_file(file, self.value, self.showing_base_paths)
        self.set_value(new_path)
        self.filter_bind.update_in_view(self.value)

        self.valid_selection_bind.update_in_view(self.model.valid_selection(new_path))
        self.populate_file_list()
