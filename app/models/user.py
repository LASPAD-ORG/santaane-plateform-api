from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False, index=True)
    email_verified: bool = Field(default=False, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    full_name: str = Field(max_length=150, nullable=False)
    country_id: Optional[int] = Field(default=None, foreign_key="countries.id")
    city_id: Optional[int] = Field(default=None, foreign_key="cities.id")
    timezone: Optional[str] = Field(max_length=50, default=None)
    profile_photo: Optional[str] = Field(max_length=255, default=None)
    orcid_id: Optional[str] = Field(max_length=50, default=None)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    country: Optional["Country"] = Relationship(back_populates="users")
    city: Optional["City"] = Relationship(back_populates="users")

