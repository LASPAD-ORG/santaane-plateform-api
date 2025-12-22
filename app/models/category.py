"""
Category model - Manuscript categories/classifications
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime



class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False, unique=True, index=True)
    description: Optional[str] = Field(default=None)
    parent_id: Optional[int] = Field(default=None, foreign_key="categories.id")  # Hierarchical categories
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    children: List["Category"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    parent: Optional["Category"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Category.parent_id"}
    )
