from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Country(SQLModel, table=True):
    __tablename__ = "countries"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, nullable=False)
    code: Optional[str] = Field(max_length=10, unique=True, default=None)  # ex: "SN"
    
    # Relationships
    cities: List["City"] = Relationship(back_populates="country")  # toutes les villes du pays
    users: List["User"] = Relationship(back_populates="country")  # tous les users du pays
