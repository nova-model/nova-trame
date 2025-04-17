"""View model for MVVM demo of DataSelector."""

from typing import Any, Dict

from nova.mvvm.interface import BindingInterface
from tests.gallery.models.data_selector import DataSelectorState


class DataSelectorVM:
    """View model for MVVM demo of FileUpload."""

    def __init__(self, binding: BindingInterface) -> None:
        self.model = DataSelectorState()
        self.model_bind = binding.new_bind(self.model, callback_after_update=self.on_update)

    def on_update(self, data: Dict[str, Any]) -> None:
        print("selected files:", self.model.selected_files)
