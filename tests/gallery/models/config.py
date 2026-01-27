"""Pydantic model for testing validation."""

from typing import Dict, List, Union

from pydantic import BaseModel, Field, field_validator


class Config(BaseModel):
    """Pydantic model for testing validation."""

    autoscroll: str = Field(default="", title="Autoscroller")
    local_storage_test: str = Field(default="", title="Local Storage")
    nested: Dict[str, str] = Field(default={"selected_file": ""})
    select1: List[str] = Field(default=[], title="Select")
    select2: List[str] = Field(default=[], title="Select")
    selected_file: str = Field(default="", title="Selected File")
    selected_folder: str = Field(default="", title="Selected Folder")
    snackbar: bool = Field(default=True)
    active_tab: int = Field(default=0)
    debounce_rate: int = Field(default=1000, title="Debounce Rate")
    debounce: str = Field(
        default="",
        description="This field is debounced and will not update its state until you've stopped typing for 1 second.",
        title="Debounced Field",
    )
    radio_items: List[Dict[str, Union[str, int]]] = Field(
        default=[{"title": "Item 1", "value": 1}, {"title": "Item 2", "value": 2}]
    )
    throttle: str = Field(
        default="",
        description="This field is throttled and will only update its state every 1 second.",
        title="Throttled Field",
    )
    value: int = Field(default=0, description="This field is validated via Pydantic.", title="Pydantic Field")

    @field_validator("debounce", mode="after")
    @classmethod
    def on_debounce(cls, text: str) -> str:
        if text:
            print(f"received debounced update: {text}")

        return text

    @field_validator("throttle", mode="after")
    @classmethod
    def on_throttle(cls, text: str) -> str:
        if text:
            print(f"received throttled update: {text}")

        return text
