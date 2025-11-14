"""
Pydantic schemas for laboratories module.
All API request/response schemas use camelCase for field names.
"""
from pydantic import Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema, TimestampSchema
from app.models.enums import EditorRole


# Laboratory Schemas

class LaboratoryBase(BaseSchema):
    """Base laboratory schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Laboratory name")
    description: Optional[str] = Field(None, description="Laboratory description")
    is_active: bool = Field(True, description="Whether laboratory is active")


class LaboratoryCreate(LaboratoryBase):
    """Schema for creating a new laboratory."""
    pass


class LaboratoryUpdate(BaseSchema):
    """Schema for updating an existing laboratory."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class LaboratoryResponse(LaboratoryBase, TimestampSchema):
    """Schema for laboratory response."""
    id: int = Field(..., description="Laboratory ID")

    model_config = ConfigDict(from_attributes=True)


# Editor Assignment Schemas

class EditorAssignmentCreate(BaseSchema):
    """Schema for assigning an editor to a laboratory."""
    user_id: int = Field(..., description="User ID of the editor to assign", alias="userId")
    role: EditorRole = Field(..., description="Editorial role")


class EditorInfo(BaseSchema):
    """Basic editor information."""
    id: int
    email: str
    full_name: str = Field(..., alias="fullName")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class EditorAssignmentResponse(BaseSchema):
    """Schema for editor assignment response."""
    id: int
    user_id: int = Field(..., alias="userId")
    laboratory_id: int = Field(..., alias="laboratoryId")
    role: EditorRole
    is_active: bool = Field(..., alias="isActive")
    assigned_at: datetime = Field(..., alias="assignedAt")
    assigned_by: Optional[int] = Field(None, alias="assignedBy")
    editor: Optional[EditorInfo] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class LaboratoryWithEditorsResponse(LaboratoryResponse):
    """Laboratory response with associated editors."""
    editors: List[EditorAssignmentResponse] = Field(default_factory=list, description="List of editors assigned to this laboratory")


# Available Editors Schema

class AvailableEditorResponse(BaseSchema):
    """Editor available for laboratory assignment."""
    id: int
    email: str
    full_name: str = Field(..., alias="fullName")
    is_active: bool = Field(..., alias="isActive")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
