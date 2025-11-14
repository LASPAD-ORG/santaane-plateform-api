"""
ManuscriptDiscussion model - Discussion threads for manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ManuscriptDiscussion(SQLModel, table=True):
    __tablename__ = "manuscript_discussions"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="manuscript_discussions.id")  # For threaded discussions
    subject: Optional[str] = Field(max_length=255, default=None)
    message: str = Field(nullable=False)
    is_internal: bool = Field(default=False, nullable=False)  # Internal discussion vs author-visible
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    manuscript: "Manuscript" = Relationship(back_populates="manuscript_discussions")
    user: "User" = Relationship(
        back_populates="manuscript_discussions",
        sa_relationship_kwargs={"foreign_keys": "[ManuscriptDiscussion.user_id]"}
    )
    parent: Optional["ManuscriptDiscussion"] = Relationship(
        back_populates="replies",
        sa_relationship_kwargs={"remote_side": "[ManuscriptDiscussion.id]"}
    )
    replies: list["ManuscriptDiscussion"] = Relationship(
        back_populates="parent"
    )
