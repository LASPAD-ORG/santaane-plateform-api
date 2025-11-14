"""
MentorshipActivityLog model - Activity tracking for mentorships
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import MentorshipActivityType

if TYPE_CHECKING:
    from app.models.mentorship import Mentorship
    from app.models.user import User


class MentorshipActivityLog(SQLModel, table=True):
    __tablename__ = "mentorship_activity_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    mentorship_id: int = Field(foreign_key="mentorships.id", nullable=False, index=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)

    activity_type: MentorshipActivityType = Field(nullable=False, index=True)

    description: str = Field(nullable=False)

    # Activity data - stored as TEXT instead of JSONB
    # Expected format: JSON string with activity-specific data
    activity_data: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    mentorship: "Mentorship" = Relationship(back_populates="mentorship_activity_logs")
    user: "User" = Relationship(
        back_populates="mentorship_activity_logs",
        sa_relationship_kwargs={"foreign_keys": "[MentorshipActivityLog.user_id]"}
    )
