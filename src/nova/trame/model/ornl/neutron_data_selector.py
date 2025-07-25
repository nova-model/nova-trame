"""Model implementation for DataSelector."""

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
    """Manages file system interactions for the DataSelector widget."""

    def __init__(self, state: NeutronDataSelectorState) -> None:
        super().__init__(state)
        self.state: NeutronDataSelectorState = state

    def set_binding_parameters(self, **kwargs: Any) -> None:
        super().set_binding_parameters(**kwargs)

        if "facility" in kwargs:
            self.state.facility = kwargs["facility"]
        if "instrument" in kwargs:
            self.state.instrument = kwargs["instrument"]
        if "experiment" in kwargs:
            self.state.experiment = kwargs["experiment"]

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
