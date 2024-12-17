"""Model state for RemoteFileInput."""

import os
from functools import cmp_to_key
from locale import strcoll
from typing import Any, Union


class RemoteFileInputModel:
    """Manages interactions between RemoteFileInput and the file system."""

    def __init__(self, allow_files: bool, allow_folders: bool, base_paths: list[str], extensions: list[str]) -> None:
        """Creates a new RemoteFileInputModel."""
        self.allow_files = allow_files
        self.allow_folders = allow_folders
        self.base_paths = base_paths
        self.extensions = extensions

    def get_base_paths(self) -> list[dict[str, Any]]:
        return [{"path": base_path, "directory": True} for base_path in self.base_paths]

    def scan_current_path(
        self, current_path: str, showing_all_files: bool, filter: str
    ) -> tuple[list[dict[str, Any]], bool]:
        failed = False
        filter = filter.split("/")[-1]

        try:
            if current_path and (not self.valid_subpath(current_path) or not os.path.exists(current_path)):
                raise FileNotFoundError

            files = [{"path": "..", "directory": True}]

            if os.path.isdir(current_path):
                scan_path = current_path
            else:
                scan_path = os.path.dirname(current_path)

            for entry in os.scandir(scan_path):
                if self.valid_entry(entry, showing_all_files) and (not filter or entry.name.startswith(filter)):
                    files.append({"path": entry.name, "directory": entry.is_dir()})
        except OSError:
            files = self.get_base_paths()
            failed = True

        def _sort_files(a: dict[str, Any], b: dict[str, Any]) -> int:
            if a["directory"] and not b["directory"]:
                return -1
            if b["directory"] and not a["directory"]:
                return 1

            path_a = a["path"].lower()
            path_b = b["path"].lower()

            return strcoll(path_a, path_b)

        sorted_files = sorted(files, key=cmp_to_key(_sort_files))

        return (sorted_files, failed)

    def select_file(self, file: Union[dict[str, str], str], old_path: str, showing_base_paths: bool) -> str:
        if file == "":
            return ""

        if isinstance(file, dict):
            file = file["path"]

        if not os.path.isdir(old_path):
            # If the previous selection is a file, then we need to append to its parent directory
            old_path = os.path.dirname(old_path)

        if not showing_base_paths and file != "..":
            return os.path.join(old_path, file)
        elif not showing_base_paths:
            if old_path in self.base_paths:
                return ""
            else:
                return os.path.dirname(old_path)
        else:
            return file

    def valid_entry(self, entry: os.DirEntry, showing_all_files: bool) -> bool:
        if entry.is_dir():
            return True

        if not self.allow_files:
            return False

        return showing_all_files or not self.extensions or any(entry.name.endswith(ext) for ext in self.extensions)

    def valid_selection(self, selection: str) -> bool:
        if self.valid_subpath(selection):
            if os.path.isdir(selection) and self.allow_folders:
                return True

            if os.path.isfile(selection) and self.allow_files:
                return True

        return False

    def valid_subpath(self, subpath: str) -> bool:
        if subpath == "":
            return False

        for base_path in self.base_paths:
            if subpath.startswith(base_path):
                return True

        return False
