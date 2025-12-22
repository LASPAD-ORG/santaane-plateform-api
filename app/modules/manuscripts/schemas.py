"""
Manuscripts module - Pydantic schemas
All fields use camelCase for client communication
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.enums import ManuscriptStatus


class ManuscriptSubmit(BaseModel):
    """Schema for manuscript submission"""
    title: str = Field(..., min_length=3, max_length=500)
    abstract: str = Field(..., min_length=10)
    keywords: Optional[str] = None
    themeId: Optional[int] = Field(None, gt=0)
    sectionId: int = Field(..., gt=0)
    languageId: int = Field(..., gt=0)
    pdfFilename: str = Field(..., description="Name of the uploaded PDF file")


class ManuscriptResponse(BaseModel):
    """Schema for manuscript response"""
    id: int
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    authorId: int
    authorName: str
    themeId: Optional[int] = None
    themeName: Optional[str] = None
    sectionId: int
    sectionName: str
    languageId: int
    languageName: str
    status: ManuscriptStatus
    pdfFilename: str
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ManuscriptListResponse(BaseModel):
    """Schema for manuscript list response"""
    manuscripts: list[ManuscriptResponse]
    total: int
