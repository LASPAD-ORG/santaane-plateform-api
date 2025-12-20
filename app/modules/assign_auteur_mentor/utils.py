"""
assign_auteur_mentor module - Utility functions
Helper functions and dependencies for mentor assignment module
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.assign_auteur_mentor.repository import MentorAssignmentRepository
from app.modules.assign_auteur_mentor.service import MentorAssignmentService


async def get_mentor_assignment_service(
    db: AsyncSession = Depends(get_db),
) -> MentorAssignmentService:
    """Dependency to get mentor assignment service instance"""
    repository = MentorAssignmentRepository(db)
    return MentorAssignmentService(repository, db)
