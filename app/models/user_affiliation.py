"""
UserAffiliation model - Junction table for user-affiliation relationships
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.affiliation import Affiliation


class UserAffiliation(SQLModel, table=True):
    __tablename__ = "user_affiliations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    affiliation_id: int = Field(foreign_key="affiliations.id", nullable=False, index=True)
    position: Optional[str] = Field(max_length=100, default=None)  # e.g., "Professor", "PhD Student"
    department: Optional[str] = Field(max_length=255, default=None)
    is_primary: bool = Field(default=False, nullable=False)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="user_affiliations")
    affiliation: "Affiliation" = Relationship(back_populates="user_affiliations")
