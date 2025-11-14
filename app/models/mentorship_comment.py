"""
MentorshipComment model - Comments within mentorship relationships
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.mentorship import Mentorship
    from app.models.user import User


class MentorshipComment(SQLModel, table=True):
    __tablename__ = "mentorship_comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    mentorship_id: int = Field(foreign_key="mentorships.id", nullable=False, index=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    comment: str = Field(nullable=False)
    is_private: bool = Field(default=False, nullable=False)  # Private vs shared with mentee
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    mentorship: "Mentorship" = Relationship(back_populates="mentorship_comments")
    user: "User" = Relationship(
        back_populates="mentorship_comments",
        sa_relationship_kwargs={"foreign_keys": "[MentorshipComment.user_id]"}
    )
