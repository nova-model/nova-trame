"""ONCat backend for NeutronDataSelector."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from natsort import natsorted
from pydantic import Field
from pyoncat import CLIENT_CREDENTIALS_FLOW, ONCat

from .neutron_data_selector import NeutronDataSelectorModel, NeutronDataSelectorState


class ONCatDataSelectorState(NeutronDataSelectorState):
    """Selection state for identifying datafiles."""

    projection: List[str] = Field(default=[])


class ONCatDataSelectorModel(NeutronDataSelectorModel):
    """ONCat backend for NeutronDataSelector."""

    def __init__(
        self,
        state: ONCatDataSelectorState,
        facility: str,
        instrument: str,
        extensions: List[str],
        projection: Optional[List[str]],
    ) -> None:
        super().__init__(state, facility, instrument, extensions)
        self.state: ONCatDataSelectorState

        if projection:
            self.state.projection = projection

        # TODO: use proxy server
        self.oncat_client = ONCat(
            "https://oncat.ornl.gov",
            client_id=os.environ.get("ONCAT_CLIENT_ID", ""),
            client_secret=os.environ.get("ONCAT_CLIENT_SECRET", ""),
            flow=CLIENT_CREDENTIALS_FLOW,
        )

    def get_facilities(self) -> List[str]:
        facilities = []
        for facility_data in self.oncat_client.Facility.list(projection=["name"]):
            facilities.append(facility_data.name)
        return natsorted(facilities)

    def get_instruments(self) -> List[str]:
        if not self.state.facility:
            return []

        instruments = []
        for instrument_data in self.oncat_client.Instrument.list(facility=self.state.facility, projection=["id"]):
            instruments.append(instrument_data.id)
        return natsorted(instruments)

    def get_experiments(self) -> List[str]:
        if not self.state.facility or not self.state.instrument:
            return []

        experiments = []
        for experiment_data in self.oncat_client.Experiment.list(
            facility=self.state.facility, instrument=self.state.instrument, projection=["name"]
        ):
            experiments.append(experiment_data.name)
        return natsorted(experiments)

    def get_directories(self, _: Optional[Path] = None) -> List[Dict[str, Any]]:
        return []

    def get_datafiles(self, *args: Any, **kwargs: Any) -> List[str]:
        if not self.state.facility or not self.state.instrument or not self.state.experiment:
            return []

        projection = ["location"] + self.state.projection

        datafiles = []
        for datafile_data in self.oncat_client.Datafile.list(
            facility=self.state.facility,
            instrument=self.state.instrument,
            experiment=self.state.experiment,
            projection=projection,
        ):
            path = datafile_data.location
            if self.state.extensions:
                for extension in self.state.extensions:
                    if path.lower().endswith(extension):
                        datafiles.append(path)
            else:
                datafiles.append(path)
        return natsorted(datafiles)
