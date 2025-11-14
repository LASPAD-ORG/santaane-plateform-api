"""
ReviewResponse model - Reviewer submissions/responses
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from app.models.enums import ReviewRecommendation

if TYPE_CHECKING:
    from app.models.review_assignment import ReviewAssignment
    from app.models.review_comment import ReviewComment


class ReviewResponse(SQLModel, table=True):
    __tablename__ = "review_responses"

    id: Optional[int] = Field(default=None, primary_key=True)
    review_assignment_id: int = Field(foreign_key="review_assignments.id", nullable=False, index=True)

    # Review content - stored as TEXT instead of JSONB
    # Expected format: JSON string with answers to form questions
    response: str = Field(nullable=False)

    # Overall assessment
    recommendation: ReviewRecommendation = Field(nullable=False)

    overall_comment: Optional[str] = Field(default=None)
    confidential_comment: Optional[str] = Field(default=None)  # For editors only

    # Tracking
    is_submitted: bool = Field(default=False, nullable=False)
    submitted_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    review_assignment: "ReviewAssignment" = Relationship(back_populates="review_responses")
    review_comments: List["ReviewComment"] = Relationship(back_populates="review_response")
