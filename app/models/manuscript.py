"""
Manuscript model - Main manuscript entity with lifecycle tracking
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from app.models.enums import ManuscriptStatus

# Import réel pour link_model
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.theme import Theme
    from app.models.section import Section
    from app.models.language import Language


class Manuscript(SQLModel, table=True):
    __tablename__ = "manuscripts"

    # --- Identité ---
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=500, nullable=False, index=True)
    abstract: Optional[str] = Field(default=None)
    keywords: Optional[str] = Field(default=None)

    # --- Relations FK ---
    author_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    theme_id: Optional[int] = Field(default=None, foreign_key="themes.id", index=True)
    section_id: int = Field(foreign_key="sections.id", nullable=False, index=True)
    language_id: int = Field(foreign_key="languages.id", nullable=False, index=True)

    # --- Workflow ---
    status: ManuscriptStatus = Field(default=ManuscriptStatus.SUBMITTED, nullable=False, index=True)

    # --- PDF obligatoire ---
    pdf_filename: str = Field(max_length=255, nullable=False)

    # --- Dates métier ---
    last_revision_at: Optional[datetime] = Field(default=None)
    decision_at: Optional[datetime] = Field(default=None)
    published_at: Optional[datetime] = Field(default=None)

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    )

    # =========================
    # Relations ORM
    # =========================
    author: User = Relationship(
        back_populates="manuscripts",
        sa_relationship_kwargs={"foreign_keys": "[Manuscript.author_id]"}
    )
    theme: Theme = Relationship(back_populates="manuscripts")
    section: Section = Relationship(back_populates="manuscripts")
    language: Language = Relationship(back_populates="manuscripts")

    evaluator_links: ManuscriptEvaluatorLink = Relationship(
        back_populates="manuscript",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Accès direct aux évaluateurs
    evaluators: User = Relationship(
        link_model=ManuscriptEvaluatorLink,
        sa_relationship_kwargs={
            "primaryjoin": "Manuscript.id==ManuscriptEvaluatorLink.manuscript_id",
            "secondaryjoin": "User.id==ManuscriptEvaluatorLink.evaluator_id",
            "viewonly": True
        }
    )
