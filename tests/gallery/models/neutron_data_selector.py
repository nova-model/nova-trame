"""Model for MVVM demo of NeutronDataSelector."""

from typing import List

from pydantic import BaseModel, Field


class NeutronDataSelectorBindingTest(BaseModel):
    """Model for testing binding parameters for DataSelector."""

    facility: str = Field(default="", title="Facility")
    instrument: str = Field(default="", title="Instrument")
    experiment: str = Field(default="", title="Experiment")
    allow_custom_directories: bool = Field(default=False, title="Allow Custom Directories?")


class NeutronDataSelectorState(BaseModel):
    """Model for MVVM demo of DataSelector."""

    selected_files: List[str] = Field(default=[], title="Selected Files")
