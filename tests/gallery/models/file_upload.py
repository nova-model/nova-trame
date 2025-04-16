"""Model for MVVM demo of FileUpload."""

from pydantic import BaseModel, Field


class FileUploadState(BaseModel):
    """Model for MVVM demo of FileUpload."""

    file: str = Field(default="")
