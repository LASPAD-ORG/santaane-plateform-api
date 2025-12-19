"""
assign_auteur_mentor module - API routes
"""
from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.user import User
from app.modules.assign_auteur_mentor.schemas import Assign_auteur_mentorResponse
from app.modules.assign_auteur_mentor.service import Assign_auteur_mentorService
from app.modules.assign_auteur_mentor.utils import get_assign_auteur_mentor_service

router = APIRouter(prefix="/assignAuteurMentor", tags=["Assign_auteur_mentor"])


@router.get("/", response_model=Assign_auteur_mentorResponse)
async def get_assign_auteur_mentor(
    current_user: User = Depends(get_current_user),
    service: Assign_auteur_mentorService = Depends(get_assign_auteur_mentor_service)
):
    """
    Get all assign_auteur_mentor

    Example endpoint - à compléter selon vos besoins
    """
    pass  # À compléter
    # return await service.get_assign_auteur_mentor(skip=skip, limit=limit)
