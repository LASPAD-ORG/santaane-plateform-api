"""
Laboratory model - Editorial laboratories for manuscript management
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING, List
from datetime import datetime

if TYPE_CHECKING:
    from app.models.editor_assignment import EditorAssignment
    from app.models.manuscript_editor import ManuscriptEditor


class Laboratory(SQLModel, table=True):
    __tablename__ = "laboratories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=255, nullable=False, unique=True, index=True)
    description: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    editor_assignments: List["EditorAssignment"] = Relationship(back_populates="laboratory")
    manuscript_editors: List["ManuscriptEditor"] = Relationship(back_populates="laboratory")
