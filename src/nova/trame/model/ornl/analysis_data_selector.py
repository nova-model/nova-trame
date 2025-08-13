"""Analysis cluster filesystem backend for NeutronDataSelector."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from warnings import warn

from natsort import natsorted
from pydantic import Field, model_validator
from typing_extensions import Self

from .neutron_data_selector import NeutronDataSelectorModel, NeutronDataSelectorState

CUSTOM_DIRECTORIES_LABEL = "Custom Directory"

INSTRUMENTS = {
    "HFIR": {
        "CG-1A": "CG1A",
        "DEV BEAM": "CG1B",
        "MARS": "CG1D",
        "GP-SANS": "CG2",
        "BIO-SANS": "CG3",
        "CNPDB": "CG4B",
        "CTAX": "CG4C",
        "IMAGINE": "CG4D",
        "PTAX": "HB1",
        "VERITAS": "HB1A",
        "POWDER": "HB2A",
        "HIDRA": "HB2B",
        "WAND²": "HB2C",
        "TAX": "HB3",
        "DEMAND": "HB3A",
        "NOWG": "NOWG",
        "NOWV": "NOWV",
    },
    "SNS": {
        "ARCS": "ARCS",
        "BL-0": "BL0",
        "BASIS": "BSS",
        "CNCS": "CNCS",
        "CORELLI": "CORELLI",
        "EQ-SANS": "EQSANS",
        "HYSPEC": "HYS",
        "MANDI": "MANDI",
        "NOMAD": "NOM",
        "NOWB": "NOWB",
        "NOWD": "NOWD",
        "NSE": "NSE",
        "POWGEN": "PG3",
        "LIQREF": "REF_L",
        "MAGREF": "REF_M",
        "SEQUOIA": "SEQ",
        "SNAP": "SNAP",
        "TOPAZ": "TOPAZ",
        "USANS": "USANS",
        "VENUS": "VENUS",
        "VISION": "VIS",
        "VULCAN": "VULCAN",
    },
}


class AnalysisDataSelectorState(NeutronDataSelectorState):
    """Selection state for identifying datafiles."""

    allow_custom_directories: bool = Field(default=False)
    custom_directory: str = Field(default="", title="Custom Directory")

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        valid_facilities = self.get_facilities()
        if self.facility and self.facility not in valid_facilities:
            warn(
                f"Facility '{self.facility}' could not be found. Valid options: {valid_facilities}",
                stacklevel=1,
            )

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


class AnalysisDataSelectorModel(NeutronDataSelectorModel):
    """Analysis cluster filesystem backend for NeutronDataSelector."""

    def __init__(self, state: AnalysisDataSelectorState) -> None:
        super().__init__(state)
        self.state: AnalysisDataSelectorState = state

    def set_binding_parameters(self, **kwargs: Any) -> None:
        super().set_binding_parameters(**kwargs)

        if "allow_custom_directories" in kwargs:
            self.state.allow_custom_directories = kwargs["allow_custom_directories"]

    def get_custom_directory_path(self) -> Optional[Path]:
        # Don't expose the full file system
        if not self.state.custom_directory:
            return None

        return Path(self.state.custom_directory)

    def get_experiment_directory_path(self) -> Optional[Path]:
        if not self.state.experiment:
            return None

        return Path("/") / self.state.facility / self.get_instrument_dir() / self.state.experiment

    def get_instrument_dir(self) -> str:
        return INSTRUMENTS.get(self.state.facility, {}).get(self.state.instrument, "")

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

    def get_datafiles(self, *args: Any, **kwargs: Any) -> List[Any]:
        using_custom_directory = self.state.facility == CUSTOM_DIRECTORIES_LABEL
        if self.state.experiment:
            base_path = Path("/") / self.state.facility / self.get_instrument_dir() / self.state.experiment
        elif using_custom_directory and self.state.custom_directory:
            base_path = Path(self.state.custom_directory)
        else:
            return []

        return [{"path": path} for path in self.get_datafiles_from_path(base_path)]
