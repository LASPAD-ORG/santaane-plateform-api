"""
Auth module - Database repository
Handles all database operations for authentication
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.user_role import UserRole


class AuthRepository:
    """Repository for authentication-related database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        full_name: str,
        hashed_password: str,
        profile_photo: Optional[str] = None,
        orcid_id: Optional[str] = None,
    ) -> User:
        """Create a new user"""
        user = User(
            email=email,
            full_name=full_name,
            password_hash=hashed_password,
            profile_photo=profile_photo,
            orcid_id=orcid_id
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def user_exists(self, email: str) -> bool:
        """Check if user exists by email"""
        user = await self.get_user_by_email(email)
        return user is not None
    
    async def assign_default_role_to_user(self, user_id: int, default_role_id: int):
        """Assign a default role to a user"""
        user_role = UserRole(
            user_id=user_id,
            role_id=default_role_id
        )
        self.db.add(user_role)
        await self.db.commit()
        await self.db.refresh(user_role)
        return user_role

    async def get_user_roles(self, user_id: int) -> list[str]:
        """Get role names for a user"""
        result = await self.db.execute(
            select(UserRole)
            .options(selectinload(UserRole.role))
            .where(UserRole.user_id == user_id)
        )
        user_roles = result.scalars().all()
        return [ur.role.name for ur in user_roles]
