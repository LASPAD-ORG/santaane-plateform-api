"""
assign_auteur_mentor module - Pydantic schemas
"""
from pydantic import BaseModel
from typing import Optional
from app.schemas.base import TimestampSchema


class Assign_auteur_mentorCreate(BaseModel):
    """Schema for creating a assign_auteur_mentor"""
    pass  # À compléter - ajouter les champs nécessaires


class Assign_auteur_mentorUpdate(BaseModel):
    """Schema for updating a assign_auteur_mentor"""
    pass  # À compléter - tous les champs optionnels


class Assign_auteur_mentorResponse(TimestampSchema):
    """Schema for assign_auteur_mentor response"""
    id: int
    pass  # À compléter - ajouter les champs de réponse


class PaginatedAssign_auteur_mentorResponse(BaseModel):
    """Paginated assign_auteur_mentor response"""
    items: list[Assign_auteur_mentorResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
