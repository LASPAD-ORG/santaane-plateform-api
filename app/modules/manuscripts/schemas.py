"""
Manuscripts module - Pydantic schemas
All fields use camelCase for client communication
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.enums import ManuscriptStatus, EvaluatorAssignmentStatus
from pydantic import BaseModel, Field, ConfigDict, field_validator 

class ManuscriptSubmit(BaseModel):
    """Schema for manuscript submission"""
    title: str = Field(..., min_length=3, max_length=500)
    abstract: str = Field(..., min_length=10)
    keywords: Optional[str] = None
    themeId: Optional[int] = Field(None, gt=0)
    sectionId: int = Field(..., gt=0)
    languageId: int = Field(..., gt=0)
    pdfFilename: str = Field(..., description="Name of the uploaded PDF file")
    docxFilename: Optional[str] = Field(None, description="Optional name of the uploaded DOCX file")


class ManuscriptRevision(BaseModel):
    """Schema for manuscript revision (when status is REVISION_REQUESTED)"""
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    abstract: Optional[str] = Field(None, min_length=10)
    keywords: Optional[str] = None
    themeId: Optional[int] = Field(None, gt=0)
    sectionId: Optional[int] = Field(None, gt=0)
    languageId: Optional[int] = Field(None, gt=0)
    pdfFilename: Optional[str] = Field(None, description="Name of the uploaded PDF file")
    docxFilename: Optional[str] = Field(None, description="Optional name of the uploaded DOCX file")


class ManuscriptUpdate(BaseModel):
    """Schema for manuscript update by editor/admin (all fields except status)"""
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    abstract: Optional[str] = Field(None, min_length=10)
    keywords: Optional[str] = None
    themeId: Optional[int] = Field(None, gt=0)
    sectionId: Optional[int] = Field(None, gt=0)
    languageId: Optional[int] = Field(None, gt=0)
    pdfFilename: Optional[str] = Field(None, description="Name of the uploaded PDF file")
    docxFilename: Optional[str] = Field(None, description="Optional name of the uploaded DOCX file")


class ManuscriptStatusUpdate(BaseModel):
    """Schema for updating manuscript status"""
    status: ManuscriptStatus = Field(..., description="New status (REVISION_REQUESTED, ACCEPTED, REJECTED, or PUBLISHED)")
    comment: Optional[str] = Field(None, description="Optional comment or reason for the status change (used for rejection reason or revision comments)")

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
    evaluationStatus: str  # 'not_started', 'in_progress', 'completed'


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
    docxFilename: Optional[str] = None
    evaluators: List[EvaluatorAssignment] = Field(default_factory=list)
    # Anonymisation fields
    isAnonymized: bool = Field(default=False)
    anonymizedAt: Optional[datetime] = None
    anonymizedByName: Optional[str] = None
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
    docxFilename: Optional[str] = None
    author: AuthorInfo
    # Anonymisation fields
    isAnonymized: bool = Field(default=False)
    anonymizedAt: Optional[datetime] = None
    anonymizedByName: Optional[str] = None
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
    docxFilename: Optional[str] = None
    assignmentStatus: EvaluatorAssignmentStatus
    assignedAt: datetime
    evaluationDeadline: Optional[datetime] = None
    responseAt: Optional[datetime] = None
    createdAt: datetime
    updatedAt: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
    
class EditorialVersionResponse(BaseModel):
    id: int
    versionNumber: int = Field(alias="version_number")
    filename: str
    createdAt: datetime = Field(alias="created_at")
    editorId: int = Field(alias="editor_id")
    editorName: Optional[str] = None

    @field_validator("editorName", mode="before")
    @classmethod
    def get_editor_name(cls, v, info):
        # Cette logique va chercher le nom dans l'objet 'editor' chargé via joinedload
        if info.data.get("editor"):
            return info.data["editor"].full_name # ou .name selon ton modèle User
        return "Éditeur Inconnu"

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
