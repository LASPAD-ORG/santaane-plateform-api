"""
ArchivedAnnotation - Copie figee d'une annotation, rattachee a une version archivee.
Reprend les memes colonnes que ManuscriptAnnotation, SANS les contraintes de l'original.
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, DateTime, func
from datetime import datetime
from typing import Optional


class ArchivedAnnotation(SQLModel, table=True):
    __tablename__ = "archived_annotations"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)

    # Rattachement a la version archivee
    version_id: int = Field(foreign_key="manuscript_versions.id", nullable=False, index=True)

    # References d'origine
    original_annotation_id: Optional[str] = Field(default=None, max_length=255)
    manuscript_id: int = Field(nullable=False, index=True)
    evaluator_id: int = Field(nullable=False, index=True)
    evaluator_kind: Optional[str] = Field(default=None, max_length=20)  # "internal" | "external"

    # Copie des colonnes de l'annotation
    annotation_type: Optional[str] = Field(default=None, max_length=20)
    created_by_role: Optional[str] = Field(default=None, max_length=20)
    page_number: Optional[int] = Field(default=None)
    x_position: Optional[float] = Field(default=None)
    y_position: Optional[float] = Field(default=None)
    position_data: Optional[str] = Field(default=None, sa_column=Column(Text))
    comment: Optional[str] = Field(default=None, sa_column=Column(Text))
    content_data: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Timestamps d'origine (copies)
    original_created_at: Optional[datetime] = Field(default=None)
    original_updated_at: Optional[datetime] = Field(default=None)

    archived_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )