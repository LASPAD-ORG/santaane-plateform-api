"""
Manuscripts module - Pydantic schemas
All fields use camelCase for client communication
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.enums import ManuscriptStatus, EvaluatorAssignmentStatus


class ManuscriptSubmit(BaseModel):
    """Schema for manuscript submission"""
    title: str = Field(..., min_length=3, max_length=500)
    abstract: str = Field(..., min_length=10)
    keywords: Optional[str] = None
    themeId: Optional[int] = Field(None, gt=0)
    sectionId: int = Field(..., gt=0)
    languageId: int = Field(..., gt=0)
    pdfFilename: str = Field(..., description="Name of the uploaded PDF file")


class ManuscriptRevision(BaseModel):
    """Schema for manuscript revision (when status is REVISION_REQUESTED)"""
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    abstract: Optional[str] = Field(None, min_length=10)
    keywords: Optional[str] = None
    themeId: Optional[int] = Field(None, gt=0)
    sectionId: Optional[int] = Field(None, gt=0)
    languageId: Optional[int] = Field(None, gt=0)
    pdfFilename: Optional[str] = Field(None, description="Name of the uploaded PDF file")


class ManuscriptUpdate(BaseModel):
    """Schema for manuscript update by editor/admin (all fields except status)"""
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    abstract: Optional[str] = Field(None, min_length=10)
    keywords: Optional[str] = None
    themeId: Optional[int] = Field(None, gt=0)
    sectionId: Optional[int] = Field(None, gt=0)
    languageId: Optional[int] = Field(None, gt=0)
    pdfFilename: Optional[str] = Field(None, description="Name of the uploaded PDF file")


class ManuscriptStatusUpdate(BaseModel):
    """Schema for updating manuscript status"""
    status: ManuscriptStatus = Field(..., description="New status (REVISION_REQUESTED, ACCEPTED, REJECTED, or PUBLISHED)")

    def validate_allowed_status(self) -> bool:
        """Check if status is one of the allowed values"""
        allowed_statuses = {
            ManuscriptStatus.REVISION_REQUESTED,
            ManuscriptStatus.ACCEPTED,
            ManuscriptStatus.REJECTED,
            ManuscriptStatus.PUBLISHED
        }
        return self.status in allowed_statuses


class AuthorInfo(BaseModel):
    """Schema for author information"""
    email: str
    fullName: str
    orcidId: Optional[str] = None
    bio: Optional[str] = None
    position: Optional[str] = None
    institution: Optional[str] = None


class EvaluatorAssignment(BaseModel):
    """Schema for evaluator assignment information"""
    evaluatorId: int
    evaluatorName: str
    evaluatorEmail: str
    status: EvaluatorAssignmentStatus
    assignedAt: datetime
    responseAt: Optional[datetime] = None
    evaluationDeadline: Optional[datetime] = None


class ManuscriptResponse(BaseModel):
    """Schema for manuscript response"""
    id: int
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    themeName: Optional[str] = None
    sectionName: str
    languageName: str
    status: ManuscriptStatus
    pdfFilename: str
    evaluators: List[EvaluatorAssignment] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ManuscriptDetailResponse(BaseModel):
    """Schema for detailed manuscript response with author info"""
    id: int
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    themeId: Optional[int] = None
    themeName: Optional[str] = None
    sectionId: int
    sectionName: str
    languageId: int
    languageName: str
    status: ManuscriptStatus
    pdfFilename: str
    author: AuthorInfo
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ManuscriptListResponse(BaseModel):
    """Schema for manuscript list response"""
    manuscripts: list[ManuscriptResponse]
    total: int


class EvaluatorManuscriptResponse(BaseModel):
    """Schema for manuscript response for evaluators (without author details)"""
    id: int
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    themeName: Optional[str] = None
    sectionName: str
    languageName: str
    status: ManuscriptStatus
    pdfFilename: str
    assignmentStatus: EvaluatorAssignmentStatus
    assignedAt: datetime
    evaluationDeadline: Optional[datetime] = None
    responseAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)
