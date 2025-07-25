"""ONCat backend for NeutronDataSelector."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from natsort import natsorted
from pydantic import Field
from pyoncat import CLIENT_CREDENTIALS_FLOW, ONCat

from .neutron_data_selector import NeutronDataSelectorModel, NeutronDataSelectorState

TOKEN_VARNAME = "USER_OIDC_TOKEN"
ID_VARNAME = "ONCAT_CLIENT_ID"
SECRET_VARNAME = "ONCAT_CLIENT_SECRET"


class ONCatDataSelectorState(NeutronDataSelectorState):
    """Selection state for identifying datafiles."""

    instrument_mapping: Dict[str, str] = Field(default={})
    projection: List[str] = Field(default=[])


class ONCatDataSelectorModel(NeutronDataSelectorModel):
    """ONCat backend for NeutronDataSelector."""

    def __init__(self, state: ONCatDataSelectorState) -> None:
        super().__init__(state)
        self.state: ONCatDataSelectorState = state

        user_token = os.environ.get(TOKEN_VARNAME, "")
        client_id = os.environ.get(ID_VARNAME, "")
        client_secret = os.environ.get(SECRET_VARNAME, "")
        if user_token:
            self.oncat_client = ONCat(url="https://calvera-test.ornl.gov/oncat", api_token=user_token)
        elif client_id and client_secret:
            self.oncat_client = ONCat(
                url="https://oncat.ornl.gov",
                client_id=client_id,
                client_secret=client_secret,
                flow=CLIENT_CREDENTIALS_FLOW,
            )
        else:
            raise EnvironmentError(
                f"In order to use the ONCat backend for NeutronDataSelector, you must set either {TOKEN_VARNAME} or "
                f"both {ID_VARNAME} and {SECRET_VARNAME} in your environment."
            )

    def set_binding_parameters(self, **kwargs: Any) -> None:
        super().set_binding_parameters(**kwargs)

        if "projection" in kwargs:
            self.state.projection = kwargs["projection"]

    def get_facilities(self) -> List[str]:
        facilities = []
        for facility_data in self.oncat_client.Facility.list(projection=["name"]):
            facilities.append(facility_data.name)
        return natsorted(facilities)

    def get_instruments(self) -> List[str]:
        if not self.state.facility:
            return []

        self.state.instrument_mapping = {}
        instruments = []
        for instrument_data in self.oncat_client.Instrument.list(
            facility=self.state.facility, projection=["short_name"]
        ):
            self.state.instrument_mapping[instrument_data.short_name] = instrument_data.id
            instruments.append(instrument_data.short_name)
        return natsorted(instruments)

    def get_experiments(self) -> List[str]:
        if not self.state.facility or not self.state.instrument:
            return []

        experiments = []
        for experiment_data in self.oncat_client.Experiment.list(
            facility=self.state.facility,
            instrument=self.state.instrument_mapping[self.state.instrument],
            projection=["name"],
        ):
            experiments.append(experiment_data.name)
        return natsorted(experiments)

    def get_directories(self, _: Optional[Path] = None) -> List[Dict[str, Any]]:
        return []

    def create_datafile_obj(self, data: Dict[str, Any], projection: List[str]) -> Dict[str, str]:
        new_obj = {"path": data["location"]}

        for key in projection:
            value: Any = data

            if key == "location":
                continue

            for part in key.split("."):
                try:
                    value = value[part]
                except KeyError:
                    value = ""
                    break

            new_obj[key] = value

        return new_obj

    def get_datafiles(self, *args: Any, **kwargs: Any) -> List[Any]:
        if not self.state.facility or not self.state.instrument or not self.state.experiment:
            return []

        projection = ["location"] + self.state.projection

        datafiles = []
        for datafile_data in self.oncat_client.Datafile.list(
            facility=self.state.facility,
            instrument=self.state.instrument_mapping[self.state.instrument],
            experiment=self.state.experiment,
            projection=projection,
        ):
            path = datafile_data.location
            if self.state.extensions:
                for extension in self.state.extensions:
                    if path.lower().endswith(extension):
                        datafiles.append(self.create_datafile_obj(datafile_data, projection))
            else:
                datafiles.append(self.create_datafile_obj(datafile_data, projection))
        return natsorted(datafiles, key=lambda d: d["path"])
