"""
User model - Journal users (authors, evaluators, editors)
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, DateTime, func

# Import réel pour link_model
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False, index=True)
    email_verified: bool = Field(default=False, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    full_name: str = Field(max_length=150, nullable=False)
    profile_photo: Optional[str] = Field(max_length=255, default=None)
    orcid_id: Optional[str] = Field(max_length=50, default=None)
    is_active: bool = Field(default=True, nullable=False)
    bio: Optional[str] = Field(default=None)
    position: Optional[str] = Field(default=None)
    institution: Optional[str] = Field(default=None)

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False))

    # Relations
    manuscripts: List[Manuscript] = Relationship(
        back_populates="author",
        sa_relationship_kwargs={"foreign_keys": "[Manuscript.author_id]"}
    )

    evaluated_manuscripts: List[Manuscript] = Relationship(
        link_model=ManuscriptEvaluatorLink,
        sa_relationship_kwargs={
            "primaryjoin": "User.id==ManuscriptEvaluatorLink.evaluator_id",
            "secondaryjoin": "Manuscript.id==ManuscriptEvaluatorLink.manuscript_id",
            "viewonly": True
        }
    )

    evaluator_assignments: List[ManuscriptEvaluatorLink] = Relationship(
        back_populates="assigned_by",
        sa_relationship_kwargs={"foreign_keys": "[ManuscriptEvaluatorLink.assigned_by_id]"}
    )
