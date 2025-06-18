"""Model implementation for DataSelector."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from warnings import warn

from natsort import natsorted
from pydantic import Field, field_validator, model_validator
from typing_extensions import Self

from ..data_selector import DataSelectorModel, DataSelectorState

CUSTOM_DIRECTORIES_LABEL = "Custom Directory"

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


class NeutronDataSelectorState(DataSelectorState):
    """Selection state for identifying datafiles."""

    allow_custom_directories: bool = Field(default=False)
    facility: str = Field(default="", title="Facility")
    instrument: str = Field(default="", title="Instrument")
    experiment: str = Field(default="", title="Experiment")
    custom_directory: str = Field(default="", title="Custom Directory")

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
        if self.instrument and self.facility != CUSTOM_DIRECTORIES_LABEL and self.instrument not in valid_instruments:
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
        if self.allow_custom_directories:
            facilities.append(CUSTOM_DIRECTORIES_LABEL)
        return facilities

    def get_instruments(self) -> List[str]:
        return list(INSTRUMENTS.get(self.facility, {}).keys())


class NeutronDataSelectorModel(DataSelectorModel):
    """Manages file system interactions for the DataSelector widget."""

    def __init__(
        self,
        state: NeutronDataSelectorState,
        facility: str,
        instrument: str,
        extensions: List[str],
        prefix: str,
        allow_custom_directories: bool,
    ) -> None:
        super().__init__(state, "", extensions, prefix)
        self.state: NeutronDataSelectorState = state

        self.state.facility = facility
        self.state.instrument = instrument
        self.state.extensions = extensions
        self.state.prefix = prefix
        self.state.allow_custom_directories = allow_custom_directories

    def get_facilities(self) -> List[str]:
        return natsorted(self.state.get_facilities())

    def get_instrument_dir(self) -> str:
        return INSTRUMENTS.get(self.state.facility, {}).get(self.state.instrument, "")

    def get_instruments(self) -> List[str]:
        return natsorted(self.state.get_instruments())

    def get_experiments(self) -> List[str]:
        experiments = []

        instrument_path = Path("/") / self.state.facility / self.get_instrument_dir()
        try:
            for dirname in os.listdir(instrument_path):
                if dirname.startswith("IPTS-") and os.access(instrument_path / dirname, mode=os.R_OK):
                    experiments.append(dirname)
        except OSError:
            pass

        return natsorted(experiments)

    def get_experiment_directory_path(self) -> Optional[Path]:
        if not self.state.experiment:
            return None

        return Path("/") / self.state.facility / self.get_instrument_dir() / self.state.experiment

    def get_custom_directory_path(self) -> Optional[Path]:
        # Don't expose the full file system
        if not self.state.custom_directory:
            return None

        return Path(self.state.custom_directory)

    def get_directories(self, base_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        using_custom_directory = self.state.facility == CUSTOM_DIRECTORIES_LABEL
        if base_path:
            pass
        elif using_custom_directory:
            base_path = self.get_custom_directory_path()
        else:
            base_path = self.get_experiment_directory_path()

        if not base_path:
            return []

        return self.get_directories_from_path(base_path)

    def get_datafiles(self) -> List[str]:
        if self.state.experiment:
            base_path = Path("/") / self.state.facility / self.get_instrument_dir() / self.state.experiment
        elif self.state.custom_directory:
            base_path = Path(self.state.custom_directory)
        else:
            return []

        return self.get_datafiles_from_path(base_path)

    def set_state(self, facility: Optional[str], instrument: Optional[str], experiment: Optional[str]) -> None:
        if facility is not None:
            self.state.facility = facility
        if instrument is not None:
            self.state.instrument = instrument
        if experiment is not None:
            self.state.experiment = experiment
