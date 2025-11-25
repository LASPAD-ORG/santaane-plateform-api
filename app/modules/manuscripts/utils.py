"""
manuscripts module - Utility functions
Helper functions and dependencies for manuscripts module
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.manuscripts.repository import ManuscriptRepository
from app.modules.manuscripts.service import ManuscriptService


def get_manuscript_service(db: AsyncSession = Depends(get_db)) -> ManuscriptService:
    """Dependency to get manuscript service instance"""
    repository = ManuscriptRepository(db)
    return ManuscriptService(repository)
