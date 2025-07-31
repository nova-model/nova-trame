"""Model for MVVM demo of FileUpload."""

from typing import List

from pydantic import BaseModel, Field


class FileUploadState(BaseModel):
    """Model for MVVM demo of FileUpload."""

    extensions: List[str] = Field(default=[".cif", ".nxs"])
    file: str = Field(default="")
    label: str = Field(default="Upload File")
