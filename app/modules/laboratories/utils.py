"""
Utilities and dependency injection for laboratories module.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.modules.laboratories.repository import LaboratoryRepository
from app.modules.laboratories.service import LaboratoryService


def get_laboratory_repository(db: AsyncSession = Depends(get_db)) -> LaboratoryRepository:
    """Dependency to get laboratory repository."""
    return LaboratoryRepository(db)


def get_laboratory_service(
    repository: LaboratoryRepository = Depends(get_laboratory_repository)
) -> LaboratoryService:
    """Dependency to get laboratory service."""
    return LaboratoryService(repository)
