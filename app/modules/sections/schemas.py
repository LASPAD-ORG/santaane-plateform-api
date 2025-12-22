"""
Section schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class SectionBase(BaseModel):
    """Base section schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Section name")
    signe_min: int = Field(..., gt=0, description="Minimum word count")
    signe_max: int = Field(..., gt=0, description="Maximum word count")

    @field_validator('signe_max')
    @classmethod
    def validate_signe_max(cls, v, info):
        """Validate that signe_max is greater than signe_min"""
        if 'signe_min' in info.data and v <= info.data['signe_min']:
            raise ValueError('signe_max must be greater than signe_min')
        return v


class SectionCreate(SectionBase):
    """Schema for creating a new section"""
    pass


class SectionUpdate(BaseModel):
    """Schema for updating a section"""
    name: str | None = Field(None, min_length=1, max_length=255, description="Section name")
    signe_min: int | None = Field(None, gt=0, description="Minimum word count")
    signe_max: int | None = Field(None, gt=0, description="Maximum word count")


class SectionResponse(SectionBase):
    """Schema for section response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
