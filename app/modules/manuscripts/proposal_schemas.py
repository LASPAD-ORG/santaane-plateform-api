"""
Schemas for external evaluator proposals (proposed by internal evaluators)
"""
from pydantic import Field, EmailStr
from datetime import datetime
from typing import Optional, List
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


class AssignProposalRequest(BaseSchema):
    """Schema pour affecter un evaluateur externe propose (par l'editeur)."""
    evaluation_deadline: datetime = Field(..., alias="evaluationDeadline")


class AssignProposalResponse(BaseSchema):
    """Resultat de l'affectation d'un evaluateur externe propose."""
    account_created: bool = Field(..., alias="accountCreated")
    role_added: bool = Field(..., alias="roleAdded")
    assigned: bool
    evaluator_id: int = Field(..., alias="evaluatorId")
    evaluator_email: str = Field(..., alias="evaluatorEmail")


class ProposalEnrichedResponse(BaseSchema):
    """Reponse enrichie : proposition + proposeur + statut de compte de la personne proposee."""
    id: int
    manuscript_id: int = Field(..., alias="manuscriptId")
    proposed_by_id: int = Field(..., alias="proposedById")
    proposed_by_name: Optional[str] = Field(None, alias="proposedByName")
    first_name: str = Field(..., alias="firstName")
    last_name: str = Field(..., alias="lastName")
    email: str
    status: str
    created_at: datetime = Field(..., alias="createdAt")
    has_account: bool = Field(..., alias="hasAccount")
    account_roles: List[str] = Field(default_factory=list, alias="accountRoles")
    has_evaluator_role: bool = Field(..., alias="hasEvaluatorRole")
