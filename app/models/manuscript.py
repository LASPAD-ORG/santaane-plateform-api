"""
Manuscript model - Main manuscript entity with lifecycle tracking
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from app.models.enums import ManuscriptStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.manuscript_editor import ManuscriptEditor
    from app.models.manuscript_file import ManuscriptFile
    from app.models.manuscript_version import ManuscriptVersion
    from app.models.manuscript_discussion import ManuscriptDiscussion
    from app.models.review_assignment import ReviewAssignment
    from app.models.review_decision import ReviewDecision
    from app.models.mentorship import Mentorship


class Manuscript(SQLModel, table=True):
    __tablename__ = "manuscripts"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500, nullable=False, index=True)
    abstract: Optional[str] = Field(default=None)
    keywords: Optional[str] = Field(default=None)  # Comma-separated string instead of array

    # Author and category
    author_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")

    # Lifecycle status
    status: ManuscriptStatus = Field(default=ManuscriptStatus.DRAFT, nullable=False, index=True)

    # Submission tracking
    submitted_at: Optional[datetime] = Field(default=None)
    last_revision_at: Optional[datetime] = Field(default=None)
    decision_at: Optional[datetime] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None)

    # Metadata
    version: int = Field(default=1, nullable=False)
    is_archived: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    author: "User" = Relationship(
        back_populates="manuscripts",
        sa_relationship_kwargs={"foreign_keys": "[Manuscript.author_id]"}
    )
    category: Optional["Category"] = Relationship(back_populates="manuscripts")
    manuscript_editors: List["ManuscriptEditor"] = Relationship(back_populates="manuscript")
    manuscript_files: List["ManuscriptFile"] = Relationship(back_populates="manuscript")
    manuscript_versions: List["ManuscriptVersion"] = Relationship(back_populates="manuscript")
    manuscript_discussions: List["ManuscriptDiscussion"] = Relationship(back_populates="manuscript")
    review_assignments: List["ReviewAssignment"] = Relationship(back_populates="manuscript")
    review_decisions: List["ReviewDecision"] = Relationship(
        back_populates="manuscript",
        sa_relationship_kwargs={"foreign_keys": "[ReviewDecision.manuscript_id]"}
    )
    mentorships: List["Mentorship"] = Relationship(back_populates="manuscript")
