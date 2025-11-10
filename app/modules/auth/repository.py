"""
Auth module - Database repository
Handles all database operations for authentication
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User


class AuthRepository:
    """Repository for authentication-related database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create_user(self, username: str, hashed_password: str) -> User:
        """Create a new user"""
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def user_exists(self, username: str) -> bool:
        """Check if user exists by username"""
        user = await self.get_user_by_username(username)
        return user is not None
