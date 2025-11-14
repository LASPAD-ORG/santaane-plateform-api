"""
MentorshipFeedback model - Structured feedback in mentorship
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import MentorshipFeedbackType

if TYPE_CHECKING:
    from app.models.mentorship import Mentorship
    from app.models.user import User


class MentorshipFeedback(SQLModel, table=True):
    __tablename__ = "mentorship_feedbacks"

    id: Optional[int] = Field(default=None, primary_key=True)
    mentorship_id: int = Field(foreign_key="mentorships.id", nullable=False, index=True)
    given_by: int = Field(foreign_key="users.id", nullable=False)

    # Feedback content - stored as TEXT instead of JSONB
    # Expected format: JSON string with structured feedback data
    feedback_data: str = Field(nullable=False)

    feedback_type: MentorshipFeedbackType = Field(nullable=False)

    rating: Optional[int] = Field(default=None)  # Numeric rating if applicable
    notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    mentorship: "Mentorship" = Relationship(back_populates="mentorship_feedbacks")
    author: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[MentorshipFeedback.given_by]"}
    )
