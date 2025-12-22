"""
Language model - Supported submission languages
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript


class Language(SQLModel, table=True):
    __tablename__ = "languages"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, nullable=False, unique=True, index=True)
    code: str = Field(max_length=10, nullable=False, unique=True, index=True)  # ex: fr, en

    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False))

    manuscripts: List[Manuscript] = Relationship(back_populates="language")
