"""View model for MVVM demo of FileUpload."""

import sys
from typing import Any, Dict

from nova.mvvm.interface import BindingInterface
from tests.gallery.models.file_upload import FileUploadState


class FileUploadVM:
    """View model for MVVM demo of FileUpload."""

    def __init__(self, binding: BindingInterface) -> None:
        self.model = FileUploadState()
        self.model_bind = binding.new_bind(self.model, callback_after_update=self.on_update)

    def on_update(self, data: Dict[str, Any]) -> None:
        print("file size:", sys.getsizeof(self.model.file))

    def update_view(self) -> None:
        self.model_bind.update_in_view(self.model)
