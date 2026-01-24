"""
Pydantic schemas for manuscript redactions (anonymization)
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
import json


class RedactionCreate(BaseModel):
    """Schema for creating a redaction - EDITOR only"""
    pageNumber: int = Field(..., ge=1, description="Page number (1-based)")
    xPosition: float = Field(..., description="X coordinate")
    yPosition: float = Field(..., description="Y coordinate")
    positionData: str = Field(..., description="JSON position data")
    comment: str = Field(
        default="Zone anonymisée",
        max_length=500,
        description="Description de la redaction (optionnel)"
    )
    contentData: Optional[str] = Field(None, description="JSON content data (optional)")

    @field_validator('positionData')
    @classmethod
    def validate_position_data_json(cls, v: str) -> str:
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError as e:
            raise ValueError(f"positionData must be valid JSON: {str(e)}")

    @field_validator('contentData')
    @classmethod
    def validate_content_data_json(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            json.loads(v)
            return v
        except json.JSONDecodeError as e:
            raise ValueError(f"contentData must be valid JSON: {str(e)}")


class RedactionUpdate(BaseModel):
    """Schema for updating a redaction"""
    comment: str = Field(..., min_length=1, max_length=500)


class RedactionResponse(BaseModel):
    """Schema for redaction response"""
    id: str
    manuscriptId: int
    editorId: int  # Note: pas evaluatorId car créé par EDITOR
    editorName: str
    annotationType: Literal["redaction"]
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


class AnonymizationStatusRequest(BaseModel):
    """Schema for marking manuscript as anonymized"""
    confirmAnonymized: bool = Field(
        default=True,
        description="Confirmation que l'anonymisation est complète"
    )


class AnonymizationStatusResponse(BaseModel):
    """Response after marking as anonymized"""
    manuscriptId: int
    isAnonymized: bool
    anonymizedAt: Optional[datetime] = None
    anonymizedByName: Optional[str] = None
    redactionCount: int  # Nombre de zones redactées

    class Config:
        from_attributes = True
