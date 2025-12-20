"""
assign_auteur_mentor module - Pydantic schemas for Mentor Assignment
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from app.schemas.base import TimestampSchema


class MentorAssignmentCreate(BaseModel):
    """Schema for creating a mentor assignment"""
    author_id: int = Field(..., gt=0, description="ID of the author to be assigned")
    mentor_id: int = Field(..., gt=0, description="ID of the mentor to assign")

    @field_validator("mentor_id")
    @classmethod
    def mentor_not_author(cls, v, info):
        """Ensure mentor and author are different users"""
        if "author_id" in info.data and v == info.data["author_id"]:
            raise ValueError("Mentor and author must be different users")
        return v


class MentorAssignmentUpdate(BaseModel):
    """Schema for updating a mentor assignment"""
    mentor_id: Optional[int] = Field(None, gt=0, description="ID of the new mentor")
    is_active: Optional[bool] = Field(None, description="Active status of the assignment")

    @field_validator("mentor_id")
    @classmethod
    def validate_mentor_id(cls, v):
        """Ensure mentor_id is valid if provided"""
        if v is not None and v <= 0:
            raise ValueError("Mentor ID must be positive")
        return v


class MentorAssignmentResponse(TimestampSchema):
    """Schema for mentor assignment response"""
    id: int
    author_id: int
    mentor_id: int
    assigned_by: Optional[int] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class MentorAssignmentDetailResponse(MentorAssignmentResponse):
    """Detailed mentor assignment response with user info"""
    author: Optional[dict] = Field(None, description="Author user information")
    mentor: Optional[dict] = Field(None, description="Mentor user information")
    assigner: Optional[dict] = Field(None, description="User who created the assignment")


class PaginatedMentorAssignmentResponse(BaseModel):
    """Paginated mentor assignment response"""
    items: list[MentorAssignmentResponse]
    total: int
    skip: int
    limit: int
    has_more: bool

    class Config:
        from_attributes = True


class SuccessMessageResponse(BaseModel):
    """Simple success response"""
    success: bool = True
    message: str = "Operation completed successfully"
