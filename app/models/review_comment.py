"""
ReviewComment model - Comments on reviews
"""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.review_response import ReviewResponse
    from app.models.user import User


class ReviewComment(SQLModel, table=True):
    __tablename__ = "review_comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    review_response_id: int = Field(foreign_key="review_responses.id", nullable=False, index=True)
    user_id: int = Field(foreign_key="users.id", nullable=False, index=True)
    comment: str = Field(nullable=False)
    is_internal: bool = Field(default=False, nullable=False)  # Internal vs visible to reviewer
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    review_response: "ReviewResponse" = Relationship(back_populates="review_comments")
    user: "User" = Relationship(
        back_populates="review_comments",
        sa_relationship_kwargs={"foreign_keys": "[ReviewComment.user_id]"}
    )
