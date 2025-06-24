"""View model implementation for the DataSelector widget."""

import os
from pathlib import Path
from typing import Any, Dict, List

from nova.mvvm.interface import BindingInterface
from nova.trame.model.data_selector import DataSelectorModel


class DataSelectorViewModel:
    """Manages the view state of the DataSelector widget."""

    def __init__(self, model: DataSelectorModel, binding: BindingInterface) -> None:
        self.model: DataSelectorModel = model

        self.datafiles: List[Dict[str, Any]] = []
        self.directories: List[Dict[str, Any]] = []
        self.expanded: Dict[str, List[str]] = {}

        self.state_bind = binding.new_bind(self.model.state, callback_after_update=self.on_state_updated)
        self.directories_bind = binding.new_bind()
        self.datafiles_bind = binding.new_bind()
        self.reset_bind = binding.new_bind()

    def expand_directory(self, paths: List[str]) -> None:
        if paths[-1] in self.expanded:
            return

        # Query for the new subdirectories to display in the view
        new_directories = self.model.get_directories(Path(paths[-1]))

        # Find the entry in the existing directories that corresponds to the directory to expand
        current_level: Dict[str, Any] = {}
        children: List[Dict[str, Any]] = self.directories
        for current_path in paths:
            if current_level:
                children = current_level["children"]

            for entry in children:
                if current_path == entry["path"]:
                    current_level = entry
                    break
        current_level["children"] = new_directories

        # Mark this directory as expanded and display the new content
        self.expanded[paths[-1]] = paths
        self.directories_bind.update_in_view(self.directories)

    def reexpand_directories(self) -> None:
        paths_to_expand = self.expanded.values()
        self.expanded = {}

        for paths in paths_to_expand:
            self.expand_directory(paths)

    def on_state_updated(self, results: Dict[str, Any]) -> None:
        pass

    def set_subdirectory(self, subdirectory_path: str = "") -> None:
        self.model.set_subdirectory(subdirectory_path)
        self.update_view()

    def update_view(self, refresh_directories: bool = False) -> None:
        self.state_bind.update_in_view(self.model.state)
        if not self.directories or refresh_directories:
            self.directories = self.model.get_directories()
            self.reexpand_directories()
        self.directories_bind.update_in_view(self.directories)

        self.datafiles = [
            {"path": datafile, "title": os.path.basename(datafile)} for datafile in self.model.get_datafiles()
        ]
        self.datafiles_bind.update_in_view(self.datafiles)
