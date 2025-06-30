"""Backend interface for NeutronDataSelector."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from natsort import natsorted
from pydantic import Field, field_validator

from ..data_selector import DataSelectorModel, DataSelectorState


class NeutronDataSelectorState(DataSelectorState):
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

    def get_facilities(self) -> List[str]:
        raise NotImplementedError()

    def get_instruments(self) -> List[str]:
        raise NotImplementedError()


class NeutronDataSelectorModel(DataSelectorModel):
    """Backend interface for NeutronDataSelector."""

    def __init__(
        self,
        state: NeutronDataSelectorState,
        facility: str,
        instrument: str,
        extensions: List[str],
        prefix: str = "",
    ) -> None:
        super().__init__(state, "", extensions, prefix)
        self.state: NeutronDataSelectorState = state

        self.state.facility = facility
        self.state.instrument = instrument
        self.state.extensions = extensions
        self.state.prefix = prefix

    def get_facilities(self) -> List[str]:
        return natsorted(self.state.get_facilities())

    def get_instruments(self) -> List[str]:
        return natsorted(self.state.get_instruments())

    def get_experiments(self) -> List[str]:
        raise NotImplementedError()

    def get_directories(self, base_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError()

    def get_datafiles(self, *args: Any, **kwargs: Any) -> List[str]:
        raise NotImplementedError()

    def set_state(self, facility: Optional[str], instrument: Optional[str], experiment: Optional[str]) -> None:
        if facility is not None:
            self.state.facility = facility
        if instrument is not None:
            self.state.instrument = instrument
        if experiment is not None:
            self.state.experiment = experiment
