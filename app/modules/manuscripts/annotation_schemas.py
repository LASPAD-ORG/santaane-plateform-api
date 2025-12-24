"""
Pydantic schemas for manuscript annotations
Matches the new API contract with annotation types and JSON data fields
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
import json


class AnnotationCreate(BaseModel):
    """Schema for creating a new annotation - matches CreateAnnotationRequest"""
    annotationType: Literal["text", "area", "freetext"] = Field(
        ...,
        description="Type of annotation"
    )
    pageNumber: int = Field(
        ...,
        ge=1,
        description="Page number in the PDF (1-based)"
    )
    xPosition: float = Field(
        ...,
        description="X coordinate on the page"
    )
    yPosition: float = Field(
        ...,
        description="Y coordinate on the page"
    )
    positionData: str = Field(
        ...,
        description="Stringified JSON position data"
    )
    comment: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Annotation comment (1-5000 characters)"
    )
    contentData: Optional[str] = Field(
        None,
        description="Stringified JSON content data (optional)"
    )

    @field_validator('positionData')
    @classmethod
    def validate_position_data_json(cls, v: str) -> str:
        """Validate that positionData is valid JSON"""
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError as e:
            raise ValueError(f"positionData must be valid JSON: {str(e)}")

    @field_validator('contentData')
    @classmethod
    def validate_content_data_json(cls, v: Optional[str]) -> Optional[str]:
        """Validate that contentData is valid JSON if provided"""
        if v is None:
            return v
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError as e:
            raise ValueError(f"contentData must be valid JSON: {str(e)}")


class AnnotationUpdate(BaseModel):
    """Schema for updating an existing annotation"""
    comment: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Updated comment"
    )


class AnnotationResponse(BaseModel):
    """Schema for annotation response - matches BackendAnnotation"""
    id: str
    manuscriptId: int
    evaluatorId: int
    evaluatorName: str
    annotationType: str
    pageNumber: int
    xPosition: float
    yPosition: float
    positionData: str
    comment: str
    contentData: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
