"""Model implementation for DataSelector."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from natsort import natsorted
from pydantic import BaseModel, Field


class DataSelectorState(BaseModel, validate_assignment=True):
    """Selection state for identifying datafiles."""

    directory: str = Field(default="")
    extensions: List[str] = Field(default=[])
    subdirectory: str = Field(default="")


class DataSelectorModel:
    """Manages file system interactions for the DataSelector widget."""

    def __init__(self, state: DataSelectorState) -> None:
        self.state: DataSelectorState = state

    def set_binding_parameters(self, **kwargs: Any) -> None:
        if "directory" in kwargs:
            self.state.directory = kwargs["directory"]
        if "extensions" in kwargs:
            self.state.extensions = kwargs["extensions"]
        if "subdirectory" in kwargs:
            self.state.subdirectory = kwargs["subdirectory"]

    def sort_directories(self, directories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Sort the current level of dictionaries
        sorted_dirs = natsorted(directories, key=lambda x: x["title"])

        # Process each sorted item to sort their children
        for item in sorted_dirs:
            if "children" in item and isinstance(item["children"], list):
                item["children"] = self.sort_directories(item["children"])

        return sorted_dirs

    def get_directories_from_path(self, base_path: Path) -> List[Dict[str, Any]]:
        directories = []
        try:
            for dirpath, dirs, _ in os.walk(base_path):
                # Get the relative path from the start path
                path_parts = os.path.relpath(dirpath, base_path).split(os.sep)

                if len(path_parts) > 1:
                    dirs.clear()
                elif path_parts != ["."]:
                    # Subdirectories are fully queried upon being opened, so we only need to query one item to determine
                    # if the target directory has any children.
                    dirs[:] = dirs[:1]

                # Only create a new entry for top-level directories
                if len(path_parts) == 1 and path_parts[0] != ".":  # This indicates a top-level directory
                    current_dir = {"path": dirpath, "title": path_parts[0]}
                    directories.append(current_dir)

                # Add subdirectories to the corresponding parent directory
                elif len(path_parts) > 1:
                    current_level: Any = directories
                    for part in path_parts[:-1]:  # Parent directories
                        for item in current_level:
                            if item["title"] == part:
                                if "children" not in item:
                                    item["children"] = []
                                current_level = item["children"]
                                break

                    # Add the last part (current directory) as a child
                    current_level.append({"path": dirpath, "title": path_parts[-1]})
        except OSError:
            pass

        return self.sort_directories(directories)

    def get_directories(self, base_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        if base_path:
            pass
        else:
            base_path = Path(self.state.directory)

        if not base_path:
            return []

        return self.get_directories_from_path(base_path)

    def get_datafiles_from_path(self, base_path: Path) -> List[str]:
        datafiles = []
        try:
            datafile_path = base_path / self.state.subdirectory

            for entry in os.scandir(datafile_path):
                if entry.is_file():
                    if self.state.extensions:
                        for extension in self.state.extensions:
                            if entry.path.lower().endswith(extension):
                                datafiles.append(entry.path)
                                break
                    else:
                        datafiles.append(entry.path)
        except OSError:
            pass

        return natsorted(datafiles)

    def get_datafiles(self) -> List[str]:
        base_path = Path(self.state.directory)

        return self.get_datafiles_from_path(base_path)

    def set_subdirectory(self, subdirectory_path: str) -> None:
        self.state.subdirectory = subdirectory_path
