"""
Theme schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ThemeBase(BaseModel):
    """Base theme schema"""
    title: str = Field(..., min_length=1, max_length=255, description="Theme title")
    description: Optional[str] = Field(None, description="Theme description")
    date_limite: Optional[datetime] = Field(None, description="Deadline for theme submission")


class ThemeCreate(ThemeBase):
    """Schema for creating a new theme"""
    pass


class ThemeUpdate(BaseModel):
    """Schema for updating a theme"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Theme title")
    description: Optional[str] = Field(None, description="Theme description")
    date_limite: Optional[datetime] = Field(None, description="Deadline for theme submission")


class ThemeResponse(ThemeBase):
    """Schema for theme response"""
    id: int
    created_at: datetime
    updated_at: datetime
    date_limite: Optional[datetime] = Field(None, description="Deadline for theme submission")

    class Config:
        from_attributes = True
