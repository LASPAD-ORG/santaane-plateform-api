"""
Mentor Assignment model - Author to Mentor assignment relationships
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User


class MentorAssignment(SQLModel, table=True):
    __tablename__ = "mentor_assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    mentor_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    assigned_by: Optional[int] = Field(default=None, foreign_key="users.id")
    is_active: bool = Field(default=True, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    author: "User" = Relationship(
        back_populates="mentor_assignments_as_author",
        sa_relationship_kwargs={"foreign_keys": "MentorAssignment.author_id"}
    )
    mentor: "User" = Relationship(
        back_populates="mentor_assignments_as_mentor",
        sa_relationship_kwargs={"foreign_keys": "MentorAssignment.mentor_id"}
    )
    assigner: Optional["User"] = Relationship(
        back_populates="mentor_assignments_created",
        sa_relationship_kwargs={"foreign_keys": "MentorAssignment.assigned_by"}
    )
