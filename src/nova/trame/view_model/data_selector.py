"""View model implementation for the DataSelector widget."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from nova.mvvm.interface import BindingInterface
from nova.trame.model.data_selector import DataSelectorModel


class DataSelectorViewModel:
    """Manages the view state of the DataSelector widget."""

    def __init__(self, model: DataSelectorModel, binding: BindingInterface) -> None:
        self.model = model

        self.datafiles: List[Dict[str, Any]] = []
        self.directories: List[Dict[str, Any]] = []
        self.expanded: List[str] = []

        self.state_bind = binding.new_bind(self.model.state, callback_after_update=self.on_state_updated)
        self.facilities_bind = binding.new_bind()
        self.instruments_bind = binding.new_bind()
        self.experiments_bind = binding.new_bind()
        self.directories_bind = binding.new_bind()
        self.datafiles_bind = binding.new_bind()
        self.reset_bind = binding.new_bind()

    def expand_directory(self, paths: List[str]) -> None:
        if paths[-1] in self.expanded:
            return

        # TODO: refactor/clean this up as it's confusing
        new_directories = self.model.get_directories(Path(paths[-1]))
        current_level: Any = self.directories
        for current_path in paths:
            if isinstance(current_level, Dict):
                current_level = current_level["children"]

            for entry in current_level:
                if current_path == entry["path"]:
                    current_level = entry
                    break
        current_level["children"] = new_directories
        self.expanded.append(paths[-1])
        self.directories_bind.update_in_view(self.directories)

    def set_directory(self, directory_path: str = "") -> None:
        self.model.set_directory(directory_path)
        self.update_view()

    def set_state(self, facility: Optional[str], instrument: Optional[str], experiment: Optional[str]) -> None:
        self.model.set_state(facility, instrument, experiment)
        self.update_view()

    def reset(self) -> None:
        self.model.set_directory("")
        self.directories = self.model.get_directories()
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

    def update_view(self) -> None:
        self.state_bind.update_in_view(self.model.state)
        self.facilities_bind.update_in_view(self.model.get_facilities())
        self.instruments_bind.update_in_view(self.model.get_instruments())
        self.experiments_bind.update_in_view(self.model.get_experiments())
        self.directories_bind.update_in_view(self.directories)

        self.datafiles = [
            {"path": datafile, "title": os.path.basename(datafile)} for datafile in self.model.get_datafiles()
        ]
        self.datafiles_bind.update_in_view(self.datafiles)
