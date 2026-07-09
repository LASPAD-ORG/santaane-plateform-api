"""
Schemas for external evaluator proposals (proposed by internal evaluators)
"""
from pydantic import Field, EmailStr
from datetime import datetime
from app.schemas.base import BaseSchema


class ProposalCreate(BaseSchema):
    """Schema pour proposer un évaluateur externe (par l'évaluateur interne)."""
    first_name: str = Field(..., min_length=1, max_length=100, alias="firstName")
    last_name: str = Field(..., min_length=1, max_length=100, alias="lastName")
    email: EmailStr = Field(..., description="Email de l'évaluateur externe proposé")


class ProposalResponse(BaseSchema):
    """Schema de réponse pour une proposition d'évaluateur externe."""
    id: int
    manuscript_id: int = Field(..., alias="manuscriptId")
    proposed_by_id: int = Field(..., alias="proposedById")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email: str
    status: str
    created_at: datetime = Field(..., alias="createdAt")