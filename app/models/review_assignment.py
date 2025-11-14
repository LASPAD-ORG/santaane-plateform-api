"""
ReviewAssignment model - Assignment of reviewers to manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from app.models.enums import ReviewAssignmentStatus

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User
    from app.models.review_response import ReviewResponse


class ReviewAssignment(SQLModel, table=True):
    __tablename__ = "review_assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    reviewer_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    assigned_by: int = Field(foreign_key="users.id", nullable=False)

    # Review tracking
    status: ReviewAssignmentStatus = Field(default=ReviewAssignmentStatus.PENDING, nullable=False, index=True)

    due_date: Optional[datetime] = Field(default=None)
    accepted_at: Optional[datetime] = Field(default=None)
    declined_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    # Metadata
    invitation_message: Optional[str] = Field(default=None)
    decline_reason: Optional[str] = Field(default=None)
    is_anonymous: bool = Field(default=True, nullable=False)  # Anonymous review
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    manuscript: "Manuscript" = Relationship(back_populates="review_assignments")
    reviewer: "User" = Relationship(
        back_populates="review_assignments",
        sa_relationship_kwargs={"foreign_keys": "[ReviewAssignment.reviewer_id]"}
    )
    assigner: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ReviewAssignment.assigned_by]"}
    )
    review_responses: List["ReviewResponse"] = Relationship(back_populates="review_assignment")
