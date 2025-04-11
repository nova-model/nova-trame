"""Model implementation for DataSelector."""

import os
from pathlib import Path
from typing import List, Optional
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


def get_facilities() -> List[str]:
    return list(INSTRUMENTS.keys())


def get_instruments(facility: str) -> List[str]:
    return list(INSTRUMENTS.get(facility, {}).keys())


class DataSelectorState(BaseModel, validate_assignment=True):
    """Selection state for identifying datafiles."""

    facility: str = Field(default="", title="Facility")
    instrument: str = Field(default="", title="Instrument")
    experiment: str = Field(default="", title="Experiment")

    @field_validator("experiment", mode="after")
    @classmethod
    def validate_experiment(cls, experiment: str) -> str:
        if experiment and not experiment.startswith("IPTS-"):
            raise ValueError("experiment must begin with IPTS-")
        return experiment

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        valid_facilities = get_facilities()
        if self.facility and self.facility not in valid_facilities:
            warn(f"Facility '{self.facility}' could not be found. Valid options: {valid_facilities}", stacklevel=1)

        valid_instruments = get_instruments(self.facility)
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


class DataSelectorModel:
    """Manages file system interactions for the DataSelector widget."""

    def __init__(self, facility: str, instrument: str) -> None:
        self.state = DataSelectorState()
        self.state.facility = facility
        self.state.instrument = instrument

    def get_facilities(self) -> List[str]:
        return get_facilities()

    def get_instrument_dir(self) -> str:
        return INSTRUMENTS.get(self.state.facility, {}).get(self.state.instrument, "")

    def get_instruments(self) -> List[str]:
        return get_instruments(self.state.facility)

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

    def get_datafiles(self) -> List[str]:
        datafiles = []

        experiment_path = Path("/") / self.state.facility / self.get_instrument_dir() / self.state.experiment / "nexus"
        try:
            for fname in os.listdir(experiment_path):
                datafiles.append(str(experiment_path / fname))
        except OSError:
            pass

        return sorted(datafiles)

    def set_state(self, facility: Optional[str], instrument: Optional[str], experiment: Optional[str]) -> None:
        if facility is not None:
            self.state.facility = facility
        if instrument is not None:
            self.state.instrument = instrument
        if experiment is not None:
            self.state.experiment = experiment
