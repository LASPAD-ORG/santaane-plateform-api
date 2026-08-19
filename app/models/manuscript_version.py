"""
ManuscriptVersion - Archive d'une version anterieure d'un manuscrit.
Chaque revision (resoumission auteur) cree une version archivee AVANT ecrasement.
"""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, DateTime, func
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript


class ManuscriptVersion(SQLModel, table=True):
    __tablename__ = "manuscript_versions"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)

    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    version_number: int = Field(nullable=False, index=True)

    # Fichiers de cette version (instantane)
    pdf_filename: str = Field(max_length=255, nullable=False)
    docx_filename: Optional[str] = Field(default=None, max_length=255)
    initial_docx_filename: Optional[str] = Field(default=None, max_length=255)

    # Metadonnees de cette version (instantane)
    title: str = Field(max_length=500, nullable=False)
    abstract: Optional[str] = Field(default=None, sa_column=Column(Text))
    keywords: Optional[str] = Field(default=None, sa_column=Column(Text))

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    archived_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

    manuscript: "Manuscript" = Relationship()