"""
Affiliation model - Academic and institutional affiliations
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user_affiliation import UserAffiliation


class Affiliation(SQLModel, table=True):
    __tablename__ = "affiliations"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False, index=True)
    type: Optional[str] = Field(max_length=100, default=None)  # e.g., "University", "Research Institute"
    country: Optional[str] = Field(max_length=100, default=None)
    city: Optional[str] = Field(max_length=100, default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user_affiliations: List["UserAffiliation"] = Relationship(back_populates="affiliation")
