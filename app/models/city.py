"""
City model
"""
from __future__ import annotations

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.country import Country


class City(SQLModel, table=True):
    __tablename__ = "cities"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    country_id: int = Field(foreign_key="countries.id", nullable=False)

    # Relationships
    country: Country = Relationship(back_populates="cities")  # lien vers le pays