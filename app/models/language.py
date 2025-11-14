"""
Language model - Language reference data
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user_language import UserLanguage


class Language(SQLModel, table=True):
    __tablename__ = "languages"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False, unique=True, index=True)
    code: str = Field(max_length=10, nullable=False, unique=True)  # ISO 639-1 code (e.g., "en", "fr")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user_languages: List["UserLanguage"] = Relationship(back_populates="language")
