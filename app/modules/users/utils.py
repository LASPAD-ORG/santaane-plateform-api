"""
Utilities and dependency injection for users module.
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.modules.users.repository import UserRepository
from app.modules.users.service import UserService


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency to get user repository."""
    return UserRepository(db)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    """Dependency to get user service."""
    return UserService(repository)
