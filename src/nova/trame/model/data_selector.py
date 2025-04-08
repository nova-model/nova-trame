"""Model implementation for DataSelector."""

import os
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field

FACILITIES = ["HFIR", "SNS"]
INSTRUMENTS = {
    "HFIR": [
        "CG1A",
        "CG1B",
        "CG1D",
        "CG2",
        "CG3",
        "CG4B",
        "CG4C",
        "CG4D",
        "HB1",
        "HB1A",
        "HB2A",
        "HB2B",
        "HB2C",
        "HB3",
        "HB3A",
        "NOWG",
        "NOWV",
    ],
    "SNS": [
        "ARCS",
        "BL0",
        "BSS",
        "CNCS",
        "CORELLI",
        "EQSANS",
        "HYS",
        "LENS",
        "MANDI",
        "NOM",
        "NOWG",
        "NSE",
        "PG3",
        "REF_L",
        "REF_M",
        "SEQ",
        "SNAP",
        "TOPAZ",
        "USANS",
        "VENUS",
        "VIS",
        "VULCAN",
    ],
}


class DataSelectorState(BaseModel):
    """Selection state for identifying datafiles."""

    facility: str = Field(default="", title="Facility")
    instrument: str = Field(default="", title="Instrument")
    experiment: str = Field(default="", title="Experiment")


class DataSelectorModel:
    """Manages file system interactions for the DataSelector widget."""

    def __init__(self, facility: str, instrument: str) -> None:
        self.state = DataSelectorState()
        self.state.facility = facility
        self.state.instrument = instrument

    def get_facilities(self) -> List[str]:
        return FACILITIES

    def get_instruments(self) -> List[str]:
        return INSTRUMENTS.get(self.state.facility, [])

    def get_experiments(self) -> List[str]:
        experiments = []

        instrument_path = Path("/") / self.state.facility / self.state.instrument
        try:
            for dirname in os.listdir(instrument_path):
                if dirname.startswith("IPTS-"):
                    experiments.append(dirname)
        except FileNotFoundError:
            pass

        return experiments

    def get_datafiles(self) -> List[str]:
        datafiles = []

        experiment_path = Path("/") / self.state.facility / self.state.instrument / self.state.experiment / "nexus"
        try:
            for fname in os.listdir(experiment_path):
                datafiles.append(str(experiment_path / fname))
        except FileNotFoundError:
            pass

        return datafiles
