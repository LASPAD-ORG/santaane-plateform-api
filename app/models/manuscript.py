"""
Manuscript model - Main manuscript entity with lifecycle tracking
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.orm import Mapped
from app.models.enums import ManuscriptStatus, ManuscriptEvaluationStatus

# Import réel pour link_model
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.theme import Theme
    from app.models.section import Section
    from app.models.language import Language
    from app.models.manuscript_annotation import ManuscriptAnnotation
    from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid
    from app.models.editorial_version import EditorialVersion


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
    evaluation_status: ManuscriptEvaluationStatus = Field(
        default=ManuscriptEvaluationStatus.PENDING,
        sa_column=Column(String(50), nullable=False, index=True),
        description="Statut du processus d'évaluation par les évaluateurs"
    )

    # --- PDF obligatoire ---
    pdf_filename: str = Field(max_length=255, nullable=False)

    # --- DOCX optionnel ---
    docx_filename: Optional[str] = Field(default=None, max_length=255, nullable=True)

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

    # --- Anonymisation ---
    is_anonymized: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="True si le manuscrit a été anonymisé (requis avant assignation évaluateur)"
    )
    anonymized_at: Optional[datetime] = Field(
        default=None,
        description="Date/heure de marquage comme anonymisé"
    )
    anonymized_by_id: Optional[int] = Field(
        default=None,
        foreign_key="users.id",
        description="ID de l'éditeur qui a marqué comme anonymisé"
    )

    # =========================
    # Relations ORM
    # =========================
    author: "User" = Relationship(
        back_populates="manuscripts",
        sa_relationship_kwargs={"foreign_keys": "[Manuscript.author_id]"}
    )
    theme: "Theme" = Relationship(back_populates="manuscripts")
    section: "Section" = Relationship(back_populates="manuscripts")
    language: "Language" = Relationship(back_populates="manuscripts")

    evaluator_links: "ManuscriptEvaluatorLink" = Relationship(
        back_populates="manuscript",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Annotations made by evaluators
    annotations: Mapped[List["ManuscriptAnnotation"]] = Relationship(
        back_populates="manuscript",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Evaluation grids made by evaluators
    evaluation_grids: Mapped[List["ManuscriptEvaluationGrid"]] = Relationship(
        back_populates="manuscript",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Accès direct aux évaluateurs
    evaluators: "User" = Relationship(
        link_model=ManuscriptEvaluatorLink,
        sa_relationship_kwargs={
            "primaryjoin": "Manuscript.id==ManuscriptEvaluatorLink.manuscript_id",
            "secondaryjoin": "User.id==ManuscriptEvaluatorLink.evaluator_id",
            "viewonly": True
        }
    )

    # Éditeur qui a anonymisé
    anonymized_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Manuscript.anonymized_by_id]"}
    )
    
    editorial_versions: List["EditorialVersion"] = Relationship(
        back_populates="manuscript",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
