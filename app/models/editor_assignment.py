"""
EditorAssignment model - Assignment of editors to laboratories
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import EditorRole

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.laboratory import Laboratory


class EditorAssignment(SQLModel, table=True):
    __tablename__ = "editor_assignments"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    laboratory_id: int = Field(foreign_key="laboratories.id", nullable=False, index=True)
    role: EditorRole = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    assigned_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    assigned_by: Optional[int] = Field(default=None, foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: "User" = Relationship(
        back_populates="editor_assignments",
        sa_relationship_kwargs={"foreign_keys": "[EditorAssignment.user_id]"}
    )
    laboratory: "Laboratory" = Relationship(back_populates="editor_assignments")
    assigner: Optional["User"] = Relationship(
        back_populates="editor_assignments_made",
        sa_relationship_kwargs={"foreign_keys": "[EditorAssignment.assigned_by]"}
    )
