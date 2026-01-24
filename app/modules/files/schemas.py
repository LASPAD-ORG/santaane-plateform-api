"""
Pydantic schemas for file upload module.
"""
from pydantic import Field, ConfigDict
from datetime import datetime
from app.schemas.base import BaseSchema


class FileUploadResponse(BaseSchema):
    """Response after successful file upload."""
    file_id: str = Field(..., description="Unique file identifier", alias="fileId")
    file_name: str = Field(..., description="Original file name", alias="fileName")
    file_path: str = Field(..., description="Stored file path", alias="filePath")
    file_size: int = Field(..., description="File size in bytes", alias="fileSize")
    file_type: str = Field(..., description="File extension", alias="fileType")
    uploaded_at: datetime = Field(..., description="Upload timestamp", alias="uploadedAt")

    model_config = ConfigDict(populate_by_name=True)


class FileDownloadResponse(BaseSchema):
    """File download information."""
    file_name: str = Field(..., description="File name", alias="fileName")
    file_size: int = Field(..., description="File size in bytes", alias="fileSize")
    file_type: str = Field(..., description="File extension", alias="fileType")

    model_config = ConfigDict(populate_by_name=True)
