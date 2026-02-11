"""
Coauthor model - Co-authors linked to manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import Column, DateTime, func

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript


class Coauthor(SQLModel, table=True):
    __tablename__ = "coauthors"

    # --- Identité ---
    id: Optional[int] = Field(default=None, primary_key=True)

    # --- Relation avec le manuscrit ---
    manuscript_id: int = Field(foreign_key="manuscripts.id", nullable=False, index=True)

    # --- Ordre d'affichage (1 = premier co-auteur, etc.) ---
    order: int = Field(default=1, nullable=False)

    # --- Informations du co-auteur ---
    first_name: str = Field(max_length=100, nullable=False)
    last_name: str = Field(max_length=100, nullable=False)
    email: str = Field(max_length=255, nullable=False)
    institution: Optional[str] = Field(default=None, max_length=255)
    orcid_id: Optional[str] = Field(default=None, max_length=50)

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )

    # =========================
    # Relations ORM
    # =========================
    manuscript: "Manuscript" = Relationship(back_populates="coauthors")
