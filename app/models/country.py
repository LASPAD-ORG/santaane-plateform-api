"""
Country model
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.city import City


class Country(SQLModel, table=True):
    __tablename__ = "countries"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, nullable=False)
    code: Optional[str] = Field(max_length=10, unique=True, default=None)  # ex: "SN"
    
    # Relationships
    cities: City = Relationship(back_populates="country")  # toutes les villes du pays
