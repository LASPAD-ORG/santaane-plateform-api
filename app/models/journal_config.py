"""
JournalConfig model - Journal configuration settings
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class JournalConfig(SQLModel, table=True):
    __tablename__ = "journal_configs"

    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(max_length=100, nullable=False, unique=True, index=True)
    value: str = Field(nullable=False)  # Stored as string instead of JSONB
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
