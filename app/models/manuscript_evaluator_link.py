"""
ManuscriptEvaluatorLink model - Table pivot Manuscript <-> Evaluator
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Enum as SQLAlchemyEnum, String
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from app.models.enums import EvaluatorAssignmentStatus, EvaluatorKind

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


def get_utc_now():
    """Return current UTC time with timezone info"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


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
        default_factory=get_utc_now,
        nullable=False
    )

    status: EvaluatorAssignmentStatus = Field(
        sa_column=Column(
            SQLAlchemyEnum(
                EvaluatorAssignmentStatus,
                name="evaluatorassignmentstatus",
                create_constraint=True,
                native_enum=False
            ),
            nullable=False,
            default=EvaluatorAssignmentStatus.PENDING.value
        )
    )
    kind: str = Field(
        default=EvaluatorKind.EXTERNAL.value,
        sa_column=Column(
            String(20),
            nullable=False,
            server_default=EvaluatorKind.EXTERNAL.value,  # rétrocompat: liens existants = external
            index=True,
        ),
        description="Type d'assignation: 'internal' (pré-examen) ou 'external' (évaluation)",
    )

    response_at: Optional[datetime] = Field(
        default=None,
        nullable=True
    )

    evaluation_deadline: Optional[datetime] = Field(
        default=None,
        nullable=True
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
