"""Model implementation for DataSelector."""

import os
from pathlib import Path
from typing import Any, List, Optional
from warnings import warn

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self

INSTRUMENTS = {
    "HFIR": {
        "CG-1A": "CG1A",
        "CG-1B": "CG1B",
        "CG-1D": "CG1D",
        "CG-2": "CG2",
        "CG-3": "CG3",
        "CG-4B": "CG4B",
        "CG-4C": "CG4C",
        "CG-4D": "CG4D",
        "HB-1": "HB1",
        "HB-1A": "HB1A",
        "HB-2A": "HB2A",
        "HB-2B": "HB2B",
        "HB-2C": "HB2C",
        "HB-3": "HB3",
        "HB-3A": "HB3A",
        "NOW-G": "NOWG",
        "NOW-V": "NOWV",
    },
    "SNS": {
        "BL-18": "ARCS",
        "BL-0": "BL0",
        "BL-2": "BSS",
        "BL-5": "CNCS",
        "BL-9": "CORELLI",
        "BL-6": "EQSANS",
        "BL-14B": "HYS",
        "BL-11B": "MANDI",
        "BL-1B": "NOM",
        "NOW-G": "NOWG",
        "BL-15": "NSE",
        "BL-11A": "PG3",
        "BL-4B": "REF_L",
        "BL-4A": "REF_M",
        "BL-17": "SEQ",
        "BL-3": "SNAP",
        "BL-12": "TOPAZ",
        "BL-1A": "USANS",
        "BL-10": "VENUS",
        "BL-16B": "VIS",
        "BL-7": "VULCAN",
    },
}


class DataSelectorState(BaseModel, validate_assignment=True):
    """Selection state for identifying datafiles."""

    facility: str = Field(default="", title="Facility")
    instrument: str = Field(default="", title="Instrument")
    experiment: str = Field(default="", title="Experiment")
    user_directory: str = Field(default="", title="User Directory")
    directory: str = Field(default="")
    extensions: List[str] = Field(default=[])
    prefix: str = Field(default="")
    show_user_directories: bool = Field(default=False)

    @field_validator("experiment", mode="after")
    @classmethod
    def validate_experiment(cls, experiment: str) -> str:
        if experiment and not experiment.startswith("IPTS-"):
            raise ValueError("experiment must begin with IPTS-")
        return experiment

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        valid_facilities = self.get_facilities()
        if self.facility and self.facility not in valid_facilities:
            warn(f"Facility '{self.facility}' could not be found. Valid options: {valid_facilities}", stacklevel=1)

        valid_instruments = self.get_instruments()
        if self.instrument and self.instrument not in valid_instruments:
            warn(
                (
                    f"Instrument '{self.instrument}' could not be found in '{self.facility}'. "
                    f"Valid options: {valid_instruments}"
                ),
                stacklevel=1,
            )
        # Validating the experiment is expensive and will fail in our CI due to the filesystem not being mounted there.

        return self

    def get_facilities(self) -> List[str]:
        facilities = list(INSTRUMENTS.keys())
        if self.show_user_directories:
            facilities.append("User Directory")
        return facilities

    def get_instruments(self) -> List[str]:
        return list(INSTRUMENTS.get(self.facility, {}).keys())


class DataSelectorModel:
    """Manages file system interactions for the DataSelector widget."""

    def __init__(
        self, facility: str, instrument: str, extensions: List[str], prefix: str, show_user_directories: bool
    ) -> None:
        self.state = DataSelectorState()
        self.state.facility = facility
        self.state.instrument = instrument
        self.state.extensions = extensions
        self.state.prefix = prefix
        self.state.show_user_directories = show_user_directories

    def get_facilities(self) -> List[str]:
        return sorted(self.state.get_facilities())

    def get_instrument_dir(self) -> str:
        return INSTRUMENTS.get(self.state.facility, {}).get(self.state.instrument, "")

    def get_instruments(self) -> List[str]:
        return sorted(self.state.get_instruments())

    def get_experiments(self) -> List[str]:
        experiments = []

        instrument_path = Path("/") / self.state.facility / self.get_instrument_dir()
        try:
            for dirname in os.listdir(instrument_path):
                if dirname.startswith("IPTS-") and os.access(instrument_path / dirname, mode=os.R_OK):
                    experiments.append(dirname)
        except OSError:
            pass

        return sorted(experiments)

    def sort_directories(self, directories: List[Any]) -> List[Any]:
        # Sort the current level of dictionaries
        sorted_dirs = sorted(directories, key=lambda x: x["title"])

        # Process each sorted item to sort their children
        for item in sorted_dirs:
            if "children" in item and isinstance(item["children"], list):
                item["children"] = self.sort_directories(item["children"])

        return sorted_dirs

    def get_experiment_directory_path(self) -> Optional[Path]:
        if not self.state.experiment:
            return None

        return Path("/") / self.state.facility / self.get_instrument_dir() / self.state.experiment

    def get_user_directory_path(self) -> Optional[Path]:
        if not self.state.user_directory:
            return None

        return Path("/SNS/users") / self.state.user_directory

    def get_directories(self) -> List[str]:
        if self.state.facility == "User Directory":
            base_path = self.get_user_directory_path()
        else:
            base_path = self.get_experiment_directory_path()

        if not base_path:
            return []

        directories = []
        try:
            for dirpath, _, _ in os.walk(base_path):
                # Get the relative path from the start path
                path_parts = os.path.relpath(dirpath, base_path).split(os.sep)

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

    def get_datafiles(self) -> List[str]:
        datafiles = []

        try:
            if self.state.prefix:
                datafile_path = str(
                    Path("/")
                    / self.state.facility
                    / self.get_instrument_dir()
                    / self.state.experiment
                    / self.state.prefix
                )
            else:
                datafile_path = self.state.directory

            for entry in os.scandir(datafile_path):
                if entry.is_file():
                    if self.state.extensions:
                        for extension in self.state.extensions:
                            if entry.path.lower().endswith(extension):
                                datafiles.append(entry.path)
                    else:
                        datafiles.append(entry.path)
        except OSError:
            pass

        return sorted(datafiles)

    def set_directory(self, directory_path: str) -> None:
        self.state.directory = directory_path

    def set_state(self, facility: Optional[str], instrument: Optional[str], experiment: Optional[str]) -> None:
        if facility is not None:
            self.state.facility = facility
        if instrument is not None:
            self.state.instrument = instrument
        if experiment is not None:
            self.state.experiment = experiment
