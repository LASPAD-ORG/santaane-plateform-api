"""
Language schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime


class LanguageBase(BaseModel):
    """Base language schema"""
    name: str = Field(..., min_length=1, max_length=50, description="Language name")
    code: str = Field(..., min_length=2, max_length=10, description="Language code (e.g., 'en', 'fr')")


class LanguageCreate(LanguageBase):
    """Schema for creating a new language"""
    pass


class LanguageUpdate(BaseModel):
    """Schema for updating a language"""
    name: str | None = Field(None, min_length=1, max_length=50, description="Language name")
    code: str | None = Field(None, min_length=2, max_length=10, description="Language code")


class LanguageResponse(LanguageBase):
    """Schema for language response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
