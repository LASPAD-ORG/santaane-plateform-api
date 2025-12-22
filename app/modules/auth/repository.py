"""
Auth module - Database repository
Handles all database operations for authentication
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.user import User
from app.models.country import Country
from app.models.city import City
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
        """Get user by ID with relationships loaded"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.country), selectinload(User.city))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        full_name: str,
        hashed_password: str,
        country_id: Optional[int] = None,
        city_id: Optional[int] = None,
        profile_photo: Optional[str] = None,
        orcid_id: Optional[str] = None,
    ) -> User:
        """Create a new user with relationships loaded"""
        user = User(
            email=email,
            full_name=full_name,
            password_hash=hashed_password,
            country_id=country_id,
            city_id=city_id,
            profile_photo=profile_photo,
            orcid_id=orcid_id
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Load relationships (country and city)
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.country), selectinload(User.city))
            .where(User.id == user.id)
        )
        return result.scalar_one()

    async def get_country_by_id(self, country_id: int) -> Optional[Country]:
        """Get country by ID"""
        result = await self.db.execute(
            select(Country).where(Country.id == country_id)
        )
        return result.scalar_one_or_none()

    async def get_city_by_id(self, city_id: int) -> Optional[City]:
        """Get city by ID"""
        result = await self.db.execute(
            select(City).where(City.id == city_id)
        )
        return result.scalar_one_or_none()

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
