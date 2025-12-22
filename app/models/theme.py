"""
Theme model - Research themes and topics
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript


class Theme(SQLModel, table=True):
    __tablename__ = "themes"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, nullable=False, index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    manuscripts: Manuscript = Relationship(back_populates="theme")
