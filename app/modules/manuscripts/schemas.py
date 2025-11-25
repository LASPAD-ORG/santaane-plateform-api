"""
Pydantic schemas for manuscripts module.
All API request/response schemas use camelCase for field names.
"""
from pydantic import Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema, TimestampSchema
from app.models.enums import ManuscriptStatus


# ==================== Manuscript Schemas ====================

class ManuscriptCreate(BaseSchema):
    """Schema for creating a manuscript"""
    title: str = Field(..., min_length=1, max_length=500, description="Manuscript title")
    abstract: str = Field(..., min_length=1, description="Manuscript abstract")
    keywords: str = Field(..., description="Comma-separated keywords")
    category_id: int = Field(..., description="Category ID", alias="categoryId")


class ManuscriptUpdate(BaseSchema):
    """Schema for updating a manuscript"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    abstract: Optional[str] = Field(None, min_length=1)
    keywords: Optional[str] = None
    category_id: Optional[int] = Field(None, alias="categoryId")


class ManuscriptResponse(TimestampSchema):
    """Schema for manuscript response"""
    id: int
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    author_id: int = Field(..., alias="authorId")
    author_name: str = Field(..., alias="authorName")
    category_id: Optional[int] = Field(None, alias="categoryId")
    category_name: Optional[str] = Field(None, alias="categoryName")
    status: ManuscriptStatus
    submitted_at: Optional[datetime] = Field(None, alias="submittedAt")
    version: int
    is_archived: bool = Field(..., alias="isArchived")
    cover_image: Optional[str] = Field(None, alias="coverImage")

    model_config = ConfigDict(from_attributes=True)


class PaginatedManuscriptResponse(BaseSchema):
    """Paginated manuscript response"""
    data: List[ManuscriptResponse]
    pagination: dict


# ==================== Manuscript Version Schemas ====================

class ManuscriptVersionCreate(BaseSchema):
    """Schema for creating a new manuscript version"""
    title: str = Field(..., min_length=1, max_length=500)
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    changes_summary: str = Field(..., min_length=1, description="Summary of changes", alias="changesSummary")


class ManuscriptVersionResponse(BaseSchema):
    """Schema for manuscript version response"""
    id: int
    manuscript_id: int = Field(..., alias="manuscriptId")
    version_number: int = Field(..., alias="versionNumber")
    title: str
    abstract: Optional[str] = None
    keywords: Optional[str] = None
    changes_summary: Optional[str] = Field(None, alias="changesSummary")
    created_by: int = Field(..., alias="createdBy")
    created_by_name: str = Field(..., alias="createdByName")
    created_at: datetime = Field(..., alias="createdAt")
    file_url: Optional[str] = Field(None, alias="fileUrl")
    file_size: Optional[int] = Field(None, alias="fileSize")

    model_config = ConfigDict(from_attributes=True)


# ==================== Timeline Schemas ====================

class TimelineEvent(BaseSchema):
    """Schema for timeline event"""
    id: int
    type: str
    title: str
    description: str
    date: datetime
    status: Optional[str] = None
    user_id: Optional[int] = Field(None, alias="userId")
    user_name: Optional[str] = Field(None, alias="userName")


# ==================== Discussion Schemas ====================

class DiscussionCreate(BaseSchema):
    """Schema for creating a discussion"""
    subject: Optional[str] = None
    message: str = Field(..., min_length=1)


class DiscussionReplyCreate(BaseSchema):
    """Schema for replying to a discussion"""
    message: str = Field(..., min_length=1)


class DiscussionReply(BaseSchema):
    """Schema for discussion reply"""
    id: int
    manuscript_id: int = Field(..., alias="manuscriptId")
    user_id: int = Field(..., alias="userId")
    user_name: str = Field(..., alias="userName")
    user_role: str = Field(..., alias="userRole")
    parent_id: Optional[int] = Field(None, alias="parentId")
    message: str
    is_internal: bool = Field(..., alias="isInternal")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(from_attributes=True)


class DiscussionResponse(BaseSchema):
    """Schema for discussion response"""
    id: int
    manuscript_id: int = Field(..., alias="manuscriptId")
    user_id: int = Field(..., alias="userId")
    user_name: str = Field(..., alias="userName")
    user_role: str = Field(..., alias="userRole")
    parent_id: Optional[int] = Field(None, alias="parentId")
    subject: Optional[str] = None
    message: str
    is_internal: bool = Field(..., alias="isInternal")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    replies: List[DiscussionReply] = []

    model_config = ConfigDict(from_attributes=True)


# ==================== Review Comment Schemas ====================

class ReviewCommentResponse(BaseSchema):
    """Schema for review comment response"""
    id: int
    review_response_id: int = Field(..., alias="reviewResponseId")
    user_id: int = Field(..., alias="userId")
    user_name: str = Field(..., alias="userName")
    user_role: str = Field(..., alias="userRole")
    comment: str
    is_internal: bool = Field(..., alias="isInternal")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    can_reply: bool = Field(..., alias="canReply")

    model_config = ConfigDict(from_attributes=True)


# ==================== Notification Schemas ====================

class NotificationResponse(BaseSchema):
    """Schema for notification response"""
    id: int
    user_id: int = Field(..., alias="userId")
    type: str
    title: str
    message: str
    manuscript_id: Optional[int] = Field(None, alias="manuscriptId")
    manuscript_title: Optional[str] = Field(None, alias="manuscriptTitle")
    is_read: bool = Field(..., alias="isRead")
    created_at: datetime = Field(..., alias="createdAt")

    model_config = ConfigDict(from_attributes=True)


class PaginatedNotificationResponse(BaseSchema):
    """Paginated notification response"""
    data: List[NotificationResponse]
    pagination: dict


# ==================== Submit Response ====================

class SubmitManuscriptResponse(BaseSchema):
    """Schema for manuscript submission response"""
    id: int
    status: ManuscriptStatus
    submitted_at: datetime = Field(..., alias="submittedAt")
    message: str


# ==================== Delete Response ====================

class DeleteManuscriptResponse(BaseSchema):
    """Schema for manuscript deletion response"""
    message: str
