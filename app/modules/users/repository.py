"""
Data access layer for users module.
Handles all database operations for users.
"""
from sqlalchemy import select, func, or_, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.logging import logger
from app.modules.users.schemas import UserCreate, UserUpdate



class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def hard_delete(self, user_id: int) -> bool:
        """Delete a user permanently from the database."""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        logger.info(f"User hard deleted: {user.email} (ID: {user.id})")
        return True

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_with_roles(self, user_id: int) -> Optional[User]:
        """Get user with roles."""
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.user_roles).selectinload(UserRole.role)
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """
        Get all users with pagination and filtering.

        Returns:
            Tuple of (users list, total count)
        """
        # Build base query
        query = select(User).options(
            selectinload(User.user_roles).selectinload(UserRole.role)
        )

        # Apply filters
        filters = []

        if email:
            filters.append(User.email.ilike(f"%{email}%"))

        if full_name:
            filters.append(User.full_name.ilike(f"%{full_name}%"))

        if is_active is not None:
            filters.append(User.is_active == is_active)

        if role:
            # Filter by role name - need to join with user_roles and roles
            role_subquery = (
                select(UserRole.user_id)
                .join(Role, UserRole.role_id == Role.id)
                .where(Role.name == role)
            )
            filters.append(User.id.in_(role_subquery))

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(User)
        if filters:
            count_query = count_query.where(and_(*filters))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        users = result.scalars().all()

        return list(users), total

    async def get_all_evaluators(
        self,
        skip: int = 0,
        limit: int = 100,
        role_name: str = "EVALUATOR",
    ) -> Tuple[List[User], int]:
        """
        Get all users having the given evaluator role
        ('EVALUATOR' ou 'INTERNAL_EVALUATOR').

        Returns:
            Tuple of (evaluators list, total count)
        """
        # Résolution dynamique de l'ID du rôle par son nom
        role = await self.get_role_by_name(role_name)
        if role is None:
            return [], 0

        evaluator_subquery = (
            select(UserRole.user_id)
            .where(UserRole.role_id == role.id)
        )

        query = (
            select(User)
            .where(User.id.in_(evaluator_subquery))
            .options(
                selectinload(User.user_roles).selectinload(UserRole.role)
            )
        )

        count_query = (
            select(func.count())
            .select_from(User)
            .where(User.id.in_(evaluator_subquery))
        )

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        evaluators = result.scalars().all()

        return list(evaluators), total

    async def create(self, data: UserCreate, password_hash: str) -> User:
        """Create a new user."""
        user = User(
            email=data.email,
            password_hash=password_hash,
            full_name=data.full_name,
            orcid_id=data.orcid_id,
            email_verified=False,
            is_active=True
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"User created: {user.email} (ID: {user.id})")
        return user

    async def create_user_model(self, user: User) -> User:
        """Create a user from a User model instance."""
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"User created: {user.email} (ID: {user.id})")
        return user

    async def assign_role(self, user_id: int, role_id: int, assigned_by_id: int) -> None:
        """Assign a role to a user."""
        from datetime import datetime
        
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by_id,
            assigned_at=datetime.utcnow()
        )
        self.db.add(user_role)
        await self.db.commit()
        logger.info(f"Role {role_id} assigned to user {user_id}")

    async def update(self, user_id: int, data: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        # Update fields if provided
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        logger.info(f"User updated: {user.email} (ID: {user.id})")
        return user

    async def update_password(self, user_id: int, new_password_hash: str) -> bool:
        """Update user password."""
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.password_hash = new_password_hash
        await self.db.commit()

        logger.info(f"Password updated for user: {user.email} (ID: {user.id})")
        return True

    async def set_active_status(self, user_id: int, is_active: bool) -> Optional[User]:
        """Activate or deactivate a user."""
        user = await self.get_by_id(user_id)
        if not user:
            return None

        user.is_active = is_active
        await self.db.commit()
        await self.db.refresh(user)

        status = "activated" if is_active else "deactivated"
        logger.info(f"User {status}: {user.email} (ID: {user.id})")
        return user

    async def delete(self, user_id: int) -> bool:
        """
        Soft delete a user (set is_active to False).
        For hard delete, use actual deletion.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        await self.db.commit()

        logger.info(f"User soft deleted: {user.email} (ID: {user.id})")
        return True

    async def get_user_roles(self, user_id: int) -> List[Role]:
        """Get all roles for a user."""
        result = await self.db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        return list(result.scalars().all())

    async def has_role(self, user_id: int, role_name: str) -> bool:
        """Check if user has a specific role."""
        result = await self.db.execute(
            select(func.count())
            .select_from(UserRole)
            .join(Role, UserRole.role_id == Role.id)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    Role.name == role_name
                )
            )
        )
        count = result.scalar()
        return count > 0

    async def remove_all_user_roles(self, user_id: int) -> None:
        """Remove all roles for a user."""
        result = await self.db.execute(
            delete(UserRole).where(UserRole.user_id == user_id)
        )
        await self.db.commit()
        logger.info(f"All roles removed for user {user_id}")

    async def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Get role by ID."""
        result = await self.db.execute(
            select(Role).where(Role.id == role_id)
        )
        return result.scalar_one_or_none()
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name (ex. 'EVALUATOR', 'INTERNAL_EVALUATOR')."""
        result = await self.db.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()