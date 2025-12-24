"""
ManuscriptAnnotation model - Annotations made by evaluators on manuscripts
"""
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript
    from app.models.user import User


class ManuscriptAnnotation(SQLModel, table=True):
    """
    Represents an annotation made by an evaluator on a manuscript PDF.
    Each annotation is positioned at specific coordinates on a specific page.
    """
    __tablename__ = "manuscript_annotations"

    id: Optional[int] = Field(default=None, primary_key=True)
    
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
    
    # PDF position information
    page_number: int = Field(nullable=False, description="Page number in the PDF (1-based)")
    x_position: float = Field(nullable=False, description="X coordinate on the page (percentage or pixels)")
    y_position: float = Field(nullable=False, description="Y coordinate on the page (percentage or pixels)")
    
    # Annotation content
    comment: str = Field(nullable=False, description="The evaluator's comment/annotation text")
    
    # Optional: highlighted text context
    highlighted_text: Optional[str] = Field(default=None, description="Text that was highlighted/selected")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    # Relationships
    manuscript: "Manuscript" = Relationship(back_populates="annotations")
    evaluator: "User" = Relationship(back_populates="manuscript_annotations")
