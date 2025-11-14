"""
ManuscriptFile model - File attachments for manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import ManuscriptFileType

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ManuscriptFile(SQLModel, table=True):
    __tablename__ = "manuscript_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    file_path: str = Field(max_length=500, nullable=False)  # File path as string
    file_name: str = Field(max_length=255, nullable=False)
    file_type: ManuscriptFileType = Field(nullable=False)
    file_size: Optional[int] = Field(default=None)  # Size in bytes
    description: Optional[str] = Field(default=None)
    uploaded_by: int = Field(foreign_key="users.id", nullable=False)
    version: int = Field(default=1, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    manuscript: "Manuscript" = Relationship(back_populates="manuscript_files")
    uploader: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[ManuscriptFile.uploaded_by]"}
    )
