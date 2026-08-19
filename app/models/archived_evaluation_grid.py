"""
ArchivedEvaluationGrid - Copie figee d'une grille d'evaluation, rattachee a une version archivee.
Reprend les memes colonnes que ManuscriptEvaluationGrid, SANS la contrainte d'unicite
(plusieurs versions peuvent archiver la meme paire manuscrit/evaluateur).
"""
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, DateTime, func
from datetime import datetime
from typing import Optional


class ArchivedEvaluationGrid(SQLModel, table=True):
    __tablename__ = "archived_evaluation_grids"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)

    # Rattachement a la version archivee
    version_id: int = Field(foreign_key="manuscript_versions.id", nullable=False, index=True)

    # References d'origine (pour l'affichage / tracabilite)
    manuscript_id: int = Field(nullable=False, index=True)
    evaluator_id: int = Field(nullable=False, index=True)
    evaluator_kind: Optional[str] = Field(default=None, max_length=20)  # "internal" | "external"

    # Copie des criteres (memes colonnes que l'original)
    originality_of_ideas: Optional[str] = Field(default=None, sa_column=Column(Text))
    methodology_rigor: Optional[str] = Field(default=None, sa_column=Column(Text))
    theoretical_approach: Optional[str] = Field(default=None, sa_column=Column(Text))
    presentation_clarity: Optional[str] = Field(default=None, sa_column=Column(Text))
    strengths: Optional[str] = Field(default=None, sa_column=Column(Text))
    weaknesses: Optional[str] = Field(default=None, sa_column=Column(Text))
    suggestions: Optional[str] = Field(default=None, sa_column=Column(Text))
    editorial_line_fit: Optional[str] = Field(default=None, sa_column=Column(Text))
    global_opinion: Optional[str] = Field(default=None, sa_column=Column(Text))
    recommendation: Optional[str] = Field(default=None, max_length=50)

    # Timestamps d'origine (copies)
    original_created_at: Optional[datetime] = Field(default=None)
    original_updated_at: Optional[datetime] = Field(default=None)
    original_submitted_at: Optional[datetime] = Field(default=None)

    archived_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )