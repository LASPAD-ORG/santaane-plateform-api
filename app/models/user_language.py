"""
UserLanguage model - Junction table for user-language relationships
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.language import Language


class UserLanguage(SQLModel, table=True):
    __tablename__ = "user_languages"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    language_id: int = Field(foreign_key="languages.id", nullable=False, index=True)
    proficiency_level: Optional[str] = Field(max_length=50, default=None)  # e.g., "Native", "Fluent", "Intermediate"
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="user_languages")
    language: "Language" = Relationship(back_populates="user_languages")
