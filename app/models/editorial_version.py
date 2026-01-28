from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User

class EditorialVersion(SQLModel, table=True):
    __tablename__ = "editorial_versions"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    version_number: int = Field(nullable=False)
    filename: str = Field(max_length=255, nullable=False)
    
    # FK vers le manuscrit
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    
    # Qui a uploadé cette version (l'éditeur)
    editor_id: int = Field(foreign_key="users.id", nullable=False)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

    manuscript: "Manuscript" = Relationship(back_populates="editorial_versions")
    editor: "User" = Relationship()