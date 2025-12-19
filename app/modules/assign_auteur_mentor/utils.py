"""
assign_auteur_mentor module - Utility functions
Helper functions and dependencies for assign_auteur_mentor module
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.assign_auteur_mentor.repository import Assign_auteur_mentorRepository
from app.modules.assign_auteur_mentor.service import Assign_auteur_mentorService


def get_assign_auteur_mentor_service(db: AsyncSession = Depends(get_db)) -> Assign_auteur_mentorService:
    """Dependency to get assign_auteur_mentor service instance"""
    repository = Assign_auteur_mentorRepository(db)
    return Assign_auteur_mentorService(repository)
