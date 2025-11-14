"""
ManuscriptEditor model - Assignment of editors to manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import EditorRole

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.manuscript import Manuscript
    from app.models.laboratory import Laboratory


class ManuscriptEditor(SQLModel, table=True):
    __tablename__ = "manuscript_editors"

    id: Optional[int] = Field(default=None, primary_key=True)
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)
    editor_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    laboratory_id: Optional[int] = Field(default=None, foreign_key="laboratories.id")
    role: EditorRole = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    assigned_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    assigned_by: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    manuscript: "Manuscript" = Relationship(back_populates="manuscript_editors")
    editor: "User" = Relationship(
        back_populates="manuscript_editors",
        sa_relationship_kwargs={"foreign_keys": "[ManuscriptEditor.editor_id]"}
    )
    laboratory: Optional["Laboratory"] = Relationship(back_populates="manuscript_editors")
    assigner: Optional["User"] = Relationship(
        back_populates="manuscript_editor_assignments_made",
        sa_relationship_kwargs={"foreign_keys": "[ManuscriptEditor.assigned_by]"}
    )
