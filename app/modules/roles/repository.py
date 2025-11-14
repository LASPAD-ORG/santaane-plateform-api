"""
roles module - Database repository
Handles all database operations for roles
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional

from app.core.logging import get_logger
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.user import User

logger = get_logger(__name__)


class RoleRepository:
    """Repository for role database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 20):
        """Get all roles with pagination"""
        total_query = select(func.count()).select_from(Role)
        total = await self.db.scalar(total_query)

        query = select(Role).offset(skip).limit(limit).order_by(Role.id)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": skip + limit < total
        }

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name"""
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def create(self, role_data: dict) -> Role:
        """Create a new role"""
        role = Role(**role_data)
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def update(self, role: Role, update_data: dict) -> Role:
        """Update an existing role"""
        for key, value in update_data.items():
            if value is not None:
                setattr(role, key, value)

        from datetime import datetime
        role.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete(self, role: Role):
        """Delete a role"""
        await self.db.delete(role)
        await self.db.commit()

    async def role_exists(self, name: str) -> bool:
        """Check if role exists by name"""
        role = await self.get_by_name(name)
        return role is not None

    # User Role operations
    async def assign_role_to_user(
        self,
        user_id: int,
        role_id: int,
        assigned_by: Optional[int] = None
    ) -> UserRole:
        """Assign a role to a user"""
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by
        )
        self.db.add(user_role)
        await self.db.commit()
        await self.db.refresh(user_role)

        # Load the role relationship
        result = await self.db.execute(
            select(UserRole)
            .options(selectinload(UserRole.role))
            .where(UserRole.id == user_role.id)
        )
        return result.scalar_one()

    async def remove_role_from_user(self, user_id: int, role_id: int):
        """Remove a role from a user"""
        result = await self.db.execute(
            select(UserRole)
            .where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        user_role = result.scalar_one_or_none()

        if user_role:
            await self.db.delete(user_role)
            await self.db.commit()

        return user_role

    async def get_user_roles(self, user_id: int) -> list[UserRole]:
        """Get all roles for a user"""
        result = await self.db.execute(
            select(UserRole)
            .options(selectinload(UserRole.role))
            .where(UserRole.user_id == user_id)
        )
        return result.scalars().all()

    async def user_has_role(self, user_id: int, role_id: int) -> bool:
        """Check if user has a specific role"""
        result = await self.db.execute(
            select(UserRole)
            .where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        return result.scalar_one_or_none() is not None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
