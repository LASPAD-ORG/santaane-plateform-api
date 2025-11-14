"""
ManuscriptVersion model - Version history for manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ManuscriptVersion(SQLModel, table=True):
    __tablename__ = "manuscript_versions"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    version_number: int = Field(nullable=False, index=True)
    title: str = Field(max_length=500, nullable=False)
    abstract: Optional[str] = Field(default=None)
    keywords: Optional[str] = Field(default=None)  # Comma-separated string
    changes_summary: Optional[str] = Field(default=None)  # Summary of changes in this version
    created_by: int = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    manuscript: "Manuscript" = Relationship(back_populates="manuscript_versions")
    creator: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ManuscriptVersion.created_by]"}
    )
