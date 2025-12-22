"""
Section model - Sections of the journal
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
import sqlalchemy as sa

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript


class Section(SQLModel, table=True):
    __tablename__ = "sections"
    __table_args__ = (
        sa.CheckConstraint('signe_max > signe_min', name='check_signe_max_gt_min'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False, index=True)
    signe_min: int = Field(nullable=False)
    signe_max: int = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    manuscripts: List[Manuscript] = Relationship(back_populates="section")
