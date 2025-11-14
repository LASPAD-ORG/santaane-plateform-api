"""
ExpertiseDomain model - Research and academic expertise domains
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user_expertise_domain import UserExpertiseDomain


class ExpertiseDomain(SQLModel, table=True):
    __tablename__ = "expertise_domains"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False, unique=True, index=True)
    description: Optional[str] = Field(default=None)
    parent_id: Optional[int] = Field(default=None, foreign_key="expertise_domains.id")  # Hierarchical structure
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user_expertise_domains: List["UserExpertiseDomain"] = Relationship(back_populates="expertise_domain")
    children: List["ExpertiseDomain"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"remote_side": "ExpertiseDomain.id"}
    )
    parent: Optional["ExpertiseDomain"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "ExpertiseDomain.parent_id"}
    )
