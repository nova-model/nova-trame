"""View model for RemoteFileInput."""

from py_mvvm.interface import BindingInterface

from trame_facade.components.remote_file_input.model import RemoteFileInputModel


class RemoteFileInputViewModel:
    counter = 0

    def __init__(self, model: RemoteFileInputModel, binding: BindingInterface):
        self.model = model

        # Needed to keep state variables separated if this class is instantiated multiple times.
        self.id = RemoteFileInputViewModel.counter
        RemoteFileInputViewModel.counter += 1

        self.previous_value = ""
        self.showing_all_files = False
        self.showing_base_paths = True
        self.value = ""
        self.dialog_bind = binding.new_bind()
        self.file_list_bind = binding.new_bind()
        self.showing_all_bind = binding.new_bind()
        self.valid_selection_bind = binding.new_bind()
        self.on_close_bind = binding.new_bind()
        self.on_update_bind = binding.new_bind()

    def open_dialog(self):
        self.previous_value = self.value
        self.populate_file_list()

    def close_dialog(self, cancel=False):
        if cancel:
            self.value = self.previous_value
            self.on_update_bind.update_in_view(self.value)

        self.on_close_bind.update_in_view(None)

    def get_dialog_state_name(self):
        return f"facade__dialog_{self.id}"

    def get_file_list_state_name(self):
        return f"facade__file_list_{self.id}"

    def get_showing_all_state_name(self):
        return f"facade__showing_all_{self.id}"

    def get_valid_selection_state_name(self):
        return f"facade__valid_selection_{self.id}"

    def init_view(self):
        self.dialog_bind.update_in_view(False)
        self.valid_selection_bind.update_in_view(False)
        self.showing_all_bind.update_in_view(self.showing_all_files)

    def set_value(self, value):
        self.value = value

    def toggle_showing_all_files(self):
        self.showing_all_files = not self.showing_all_files
        self.showing_all_bind.update_in_view(self.showing_all_files)
        self.populate_file_list()

    def populate_file_list(self):
        files = self.scan_current_path()
        self.file_list_bind.update_in_view(files)

    def scan_current_path(self):
        files, self.showing_base_paths = self.model.scan_current_path(
            self.value, self.showing_all_files
        )

        return files

    def select_file(self, file):
        new_path = self.model.select_file(file, self.value, self.showing_base_paths)
        self.set_value(new_path)
        self.on_update_bind.update_in_view(self.value)

        self.valid_selection_bind.update_in_view(self.model.valid_selection(new_path))
        self.populate_file_list()
