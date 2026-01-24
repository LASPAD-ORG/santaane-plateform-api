"""
Manuscripts module - Utility functions
"""
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db import get_db
from app.modules.manuscripts.repository import ManuscriptRepository
from app.modules.manuscripts.service import ManuscriptService


async def get_manuscript_repository(
    session: AsyncSession = Depends(get_db)
) -> ManuscriptRepository:
    """Dependency for manuscript repository"""
    return ManuscriptRepository(session)


async def get_manuscript_service(
    repository: ManuscriptRepository = Depends(get_manuscript_repository)
) -> ManuscriptService:
    """
    Dependency for manuscript service
    
    Args:
        repository: Le repository des manuscrits
        
    Returns:
        Une instance du service de manuscrit
    """
    return ManuscriptService(repository=repository)
