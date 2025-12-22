"""
ManuscriptEvaluatorLink model - Table pivot Manuscript <-> Evaluator
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ManuscriptEvaluatorLink(SQLModel, table=True):
    __tablename__ = "manuscript_evaluators"

    manuscript_id: int = Field(
        foreign_key="manuscripts.id",
        primary_key=True
    )

    evaluator_id: int = Field(
        foreign_key="users.id",
        primary_key=True
    )

    assigned_by_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        index=True
    )

    assigned_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # Relations
    manuscript: Manuscript = Relationship(back_populates="evaluator_links")
    evaluator: User = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ManuscriptEvaluatorLink.evaluator_id]"
        }
    )
    assigned_by: User = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ManuscriptEvaluatorLink.assigned_by_id]"
        }
    )
