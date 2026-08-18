from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, DateTime, Text, func

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ManuscriptAttachment(SQLModel, table=True):
    __tablename__ = "manuscript_attachments"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)

    # FK vers le manuscrit
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)

    # Fichier stocke
    filename: str = Field(max_length=500, nullable=False)  # chemin relatif dans le storage
    original_filename: str = Field(max_length=255, nullable=False)
    content_type: Optional[str] = Field(default=None, max_length=150)
    file_size: Optional[int] = Field(default=None)

    # Metadonnees fournies par l'utilisateur
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Qui a depose la piece
    uploaded_by_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    uploaded_by_role: str = Field(max_length=20, nullable=False)  # "author" | "editor"

    # Visibilite : l'auteur peut-il voir cette piece ?
    visible_to_author: bool = Field(default=True, nullable=False, index=True)

    # Type de piece : "author_upload" | "editor_internal" | "editor_transmission"
    attachment_type: str = Field(max_length=30, nullable=False, default="author_upload", index=True)

    # Si la piece repond a une demande de l'editeur
    request_id: Optional[int] = Field(
        default=None, foreign_key="attachment_requests.id", index=True
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

    manuscript: "Manuscript" = Relationship()
    uploaded_by: "User" = Relationship()