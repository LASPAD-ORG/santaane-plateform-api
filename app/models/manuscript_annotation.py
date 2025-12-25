"""
ManuscriptAnnotation model - Annotations made by evaluators on manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text, CheckConstraint
from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ManuscriptAnnotation(SQLModel, table=True):
    """
    Represents an annotation made by an evaluator on a manuscript PDF.
    Supports multiple annotation types: text highlights, area selections, and freetext notes.
    """
    __tablename__ = "manuscript_annotations"
    __table_args__ = (
        CheckConstraint(
            "annotation_type IN ('text', 'area', 'freetext', 'redaction')",
            name="check_annotation_type"
        ),
    )

    # Primary key: UUID string
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        max_length=255,
        description="Unique identifier (UUID)"
    )

    manuscript_id: int = Field(
        foreign_key="manuscripts.id",
        nullable=False,
        index=True
    )

    evaluator_id: int = Field(
        foreign_key="users.id",
        nullable=False,
        index=True
    )

    # Annotation type
    annotation_type: str = Field(
        nullable=False,
        max_length=20,
        description="Type of annotation: 'text', 'area', 'freetext', or 'redaction'"
    )

    # Role of the creator (to distinguish EDITOR redactions from EVALUATOR annotations)
    created_by_role: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Role of creator: 'EDITOR' for redactions, 'EVALUATOR' for annotations"
    )

    # PDF position information (kept for backward compatibility and quick queries)
    page_number: int = Field(nullable=False, description="Page number in the PDF (1-based)")
    x_position: float = Field(nullable=False, description="X coordinate on the page")
    y_position: float = Field(nullable=False, description="Y coordinate on the page")

    # JSON position data (stringified)
    position_data: str = Field(
        sa_column=Column(Text, nullable=False),
        description="JSON stringified position data"
    )

    # Annotation content
    comment: str = Field(nullable=False, description="The evaluator's comment/annotation text")

    # JSON content data (replaces highlighted_text)
    content_data: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="JSON stringified content data (optional)"
    )

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    manuscript: "Manuscript" = Relationship(back_populates="annotations")
    evaluator: "User" = Relationship(back_populates="manuscript_annotations")
