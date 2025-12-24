"""
Pydantic schemas for manuscript annotations
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AnnotationCreate(BaseModel):
    """Schema for creating a new annotation"""
    pageNumber: int = Field(..., ge=1, description="Page number in the PDF (1-based)")
    xPosition: float = Field(..., description="X coordinate on the page")
    yPosition: float = Field(..., description="Y coordinate on the page")
    comment: str = Field(..., min_length=1, max_length=5000, description="Annotation comment")
    highlightedText: Optional[str] = Field(None, max_length=1000, description="Text that was highlighted")


class AnnotationUpdate(BaseModel):
    """Schema for updating an existing annotation"""
    comment: str = Field(..., min_length=1, max_length=5000, description="Updated comment")


class AnnotationResponse(BaseModel):
    """Schema for annotation response"""
    id: int
    manuscriptId: int
    evaluatorId: int
    evaluatorName: str
    pageNumber: int
    xPosition: float
    yPosition: float
    comment: str
    highlightedText: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
