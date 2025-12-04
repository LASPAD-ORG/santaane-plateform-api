"""
ReviewFormEntry model - Entrées structurées (scores/valeurs) de la grille d'évaluation
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import ReviewCriteria

if TYPE_CHECKING:
    from app.models.review_response import ReviewResponse


class ReviewFormEntry(SQLModel, table=True):
    __tablename__ = "review_form_entries"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    review_response_id: int = Field(foreign_key="review_responses.id", nullable=False, index=True)
    
    criterion: ReviewCriteria = Field(nullable=False, index=True)
    
    score_or_value: int = Field(nullable=False) 
    
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    review_response: "ReviewResponse" = Relationship(back_populates="form_entries")
