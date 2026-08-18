from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, DateTime, Text, func

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class AttachmentRequest(SQLModel, table=True):
    __tablename__ = "attachment_requests"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)

    # FK vers le manuscrit
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)

    # Ce que l'editeur demande
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Qui a fait la demande (editeur)
    requested_by_id: int = Field(foreign_key="users.id", nullable=False, index=True)

    # Statut : "pending" | "fulfilled"
    status: str = Field(max_length=20, nullable=False, default="pending", index=True)

    # Piece qui a repondu a la demande (si fournie)
    fulfilled_by_attachment_id: Optional[int] = Field(default=None)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    fulfilled_at: Optional[datetime] = Field(default=None)

    manuscript: "Manuscript" = Relationship()
    requested_by: "User" = Relationship()