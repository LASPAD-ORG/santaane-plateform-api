"""
ExternalEvaluatorProposal - Évaluateurs externes proposés par un évaluateur interne.
Purement informatif : l'éditeur reste libre de son choix final.
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ExternalEvaluatorProposal(SQLModel, table=True):
    __tablename__ = "external_evaluator_proposals"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    proposed_by_id: int = Field(foreign_key="users.id", nullable=False, index=True)

    first_name: str = Field(max_length=100, nullable=False)
    last_name: str = Field(max_length=100, nullable=False)
    email: str = Field(max_length=255, nullable=False, index=True)

    status: str = Field(
        default="proposed",
        sa_column=Column(String(20), nullable=False, server_default="proposed"),
        description="'proposed', 'converted' (compte externe créé) ou 'rejected'",
    )

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
