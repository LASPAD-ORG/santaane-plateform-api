"""
UserExpertiseDomain model - Junction table for user-expertise domain relationships
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.expertise_domain import ExpertiseDomain


class UserExpertiseDomain(SQLModel, table=True):
    __tablename__ = "user_expertise_domains"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    expertise_domain_id: int = Field(foreign_key="expertise_domains.id", nullable=False, index=True)
    proficiency_level: Optional[str] = Field(max_length=50, default=None)  # e.g., "Beginner", "Expert"
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="user_expertise_domains")
    expertise_domain: "ExpertiseDomain" = Relationship(back_populates="user_expertise_domains")
