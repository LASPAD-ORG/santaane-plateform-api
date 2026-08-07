"""
ManuscriptEvaluationGrid model - Grille d'évaluation des manuscrits par les évaluateurs
"""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, UniqueConstraint
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ManuscriptEvaluationGrid(SQLModel, table=True):
    """
    Grille d'évaluation remplie par un évaluateur pour un manuscrit.
    Un évaluateur ne peut avoir qu'une seule grille par manuscrit.
    """
    __tablename__ = "manuscript_evaluation_grids"
    __table_args__ = (
        UniqueConstraint('manuscript_id', 'evaluator_id', name='uq_manuscript_evaluator'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    manuscript_id: int = Field(
        foreign_key="manuscripts.id",
        nullable=False,
        index=True
    )

    evaluator_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        index=True
    )

    # Critères d'évaluation (tous stockés en TEXT pour supporter de longs textes)
    originality_of_ideas: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Originalité des idées et des conclusions"
    )

    methodology_rigor: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Pertinence et rigueur de la méthode, de la démarche et des références"
    )

    theoretical_approach: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Recours à des études empiriques et une approche théorique solide"
    )

    presentation_clarity: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Soin dans la présentation et la structure du texte, clarté de l'expression"
    )

    strengths: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Points forts du manuscrit"
    )

    weaknesses: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Points faibles du manuscrit"
    )

    suggestions: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Suggestions pour améliorer le texte (optionnel)"
    )

    # --- Champs spécifiques à la grille de l'évaluateur interne ---
    editorial_line_fit: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Adéquation à la ligne éditoriale (grille interne)"
    )

    global_opinion: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Avis global sur le manuscrit (grille interne)"
    )

    # Avis final
    recommendation: str = Field(
        max_length=50,
        nullable=False,
        description="Avis final. Externe: accepted_with_validation, resubmission_required, rejected. Interne: internal_accepted_after_revision, internal_to_external, internal_rejected"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    submitted_at: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Date de soumission finale (NULL = brouillon, NOT NULL = soumis)"
    )

    # Relationships
    manuscript: "Manuscript" = Relationship(back_populates="evaluation_grids")
    evaluator: "User" = Relationship(back_populates="evaluation_grids")