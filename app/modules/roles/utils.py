"""
roles module - Utility functions
Helper functions and dependencies for roles module
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.roles.repository import RoleRepository
from app.modules.roles.service import RoleService


def get_role_service(db: AsyncSession = Depends(get_db)) -> RoleService:
    """Dependency to get role service instance"""
    repository = RoleRepository(db)
    return RoleService(repository)
