"""Model for MVVM demo of DataSelector."""

from typing import List

from pydantic import BaseModel, Field


class DataSelectorState(BaseModel):
    """Model for MVVM demo of DataSelector."""

    selected_files: List[str] = Field(default=[], title="Selected Files")
    selected_neutron_files: List[str] = Field(default=[], title="Selected Neutron Datafiles")
