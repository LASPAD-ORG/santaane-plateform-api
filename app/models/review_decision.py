"""
ReviewDecision model - Editorial decisions on manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import ReviewDecisionType

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ReviewDecision(SQLModel, table=True):
    __tablename__ = "review_decisions"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    decided_by: int = Field(foreign_key="users.id", nullable=False)

    decision: ReviewDecisionType = Field(nullable=False, index=True)

    decision_letter: Optional[str] = Field(default=None)  # Letter to author
    internal_notes: Optional[str] = Field(default=None)  # Internal editor notes

    decided_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    manuscript: "Manuscript" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ReviewDecision.manuscript_id]"}
    )
    editor: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ReviewDecision.decided_by]"}
    )
