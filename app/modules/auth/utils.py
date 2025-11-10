"""
Auth module - Utility functions
Helper functions and dependencies for authentication module
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.auth.repository import AuthRepository
from app.modules.auth.service import AuthService


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get auth service instance"""
    repository = AuthRepository(db)
    return AuthService(repository)
