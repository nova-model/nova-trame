"""Model for MVVM demo of DataSelector."""

from typing import List

from pydantic import BaseModel, Field


class DataSelectorBindingTest(BaseModel):
    """Model for testing binding parameters for DataSelector."""

    directory: str = Field(default="", title="Base Directory")
    refresh_rate: int = Field(default=0, title="Refresh Rate")
    subdirectory: str = Field(default="")


class DataSelectorState(BaseModel):
    """Model for MVVM demo of DataSelector."""

    selected_files: List[str] = Field(default=[], title="Selected Files")
