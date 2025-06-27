"""View model implementation for the DataSelector widget."""

from typing import Any, Dict, Optional

from nova.mvvm.interface import BindingInterface
from nova.trame.model.ornl.neutron_data_selector import NeutronDataSelectorModel
from nova.trame.view_model.data_selector import DataSelectorViewModel


class NeutronDataSelectorViewModel(DataSelectorViewModel):
    """Manages the view state of the DataSelector widget."""

    def __init__(self, model: NeutronDataSelectorModel, binding: BindingInterface) -> None:
        super().__init__(model, binding)
        self.model: NeutronDataSelectorModel = model

        self.facilities_bind = binding.new_bind()
        self.instruments_bind = binding.new_bind()
        self.experiments_bind = binding.new_bind()

    def set_state(self, facility: Optional[str], instrument: Optional[str], experiment: Optional[str]) -> None:
        self.model.set_state(facility, instrument, experiment)
        self.update_view()

    def reset(self) -> None:
        self.model.set_subdirectory("")
        self.directories = self.model.get_directories()
        self.expanded = {}
        self.reset_bind.update_in_view(None)

    def on_state_updated(self, results: Dict[str, Any]) -> None:
        for update in results.get("updated", []):
            match update:
                case "facility":
                    self.model.set_state(facility=None, instrument="", experiment="")
                    self.reset()
                case "instrument":
                    self.model.set_state(facility=None, instrument=None, experiment="")
                    self.reset()
                case "experiment":
                    self.reset()
                case "custom_directory":
                    self.reset()
        self.update_view()

    def update_view(self, refresh_directories: bool = False) -> None:
        self.facilities_bind.update_in_view(self.model.get_facilities())
        self.instruments_bind.update_in_view(self.model.get_instruments())
        self.experiments_bind.update_in_view(self.model.get_experiments())

        super().update_view(refresh_directories)
