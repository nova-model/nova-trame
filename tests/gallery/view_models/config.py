"""View model for the config model."""

from typing import Optional

from nova.mvvm.interface import BindingInterface

from ..models.config import Config


class ConfigVM:
    """View model for the config model."""

    def __init__(self, binding: BindingInterface) -> None:
        self.config = Config()
        self.config_bind = binding.new_bind(self.config)

    def append_to_autoscroll(self, value: str) -> None:
        self.config.autoscroll += value
        self.config_bind.update_in_view(self.config)

    def get_local_storage(self) -> str:
        return self.config.local_storage_test

    def set_local_storage(self, value: Optional[str]) -> None:
        if value is not None:
            self.config.local_storage_test = value
            self.config_bind.update_in_view(self.config)
