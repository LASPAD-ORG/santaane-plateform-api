"""
Mentorship model - Mentorship relationships for manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from app.models.enums import MentorshipStatus

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User
    from app.models.mentorship_comment import MentorshipComment
    from app.models.mentorship_feedback import MentorshipFeedback
    from app.models.mentorship_activity_log import MentorshipActivityLog


class Mentorship(SQLModel, table=True):
    __tablename__ = "mentorships"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    mentor_id: int = Field(foreign_key="users.id", nullable=False, index=True)

    status: MentorshipStatus = Field(default=MentorshipStatus.ACTIVE, nullable=False, index=True)

    assigned_by: Optional[int] = Field(default=None, foreign_key="users.id")
    started_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    manuscript: "Manuscript" = Relationship(back_populates="mentorships")
    mentor: "User" = Relationship(
        back_populates="mentorships_as_mentor",
        sa_relationship_kwargs={"foreign_keys": "[Mentorship.mentor_id]"}
    )
    assigner: Optional["User"] = Relationship(
        back_populates="mentorships_assigned",
        sa_relationship_kwargs={"foreign_keys": "[Mentorship.assigned_by]"}
    )
    mentorship_comments: List["MentorshipComment"] = Relationship(back_populates="mentorship")
    mentorship_feedbacks: List["MentorshipFeedback"] = Relationship(back_populates="mentorship")
    mentorship_activity_logs: List["MentorshipActivityLog"] = Relationship(back_populates="mentorship")
