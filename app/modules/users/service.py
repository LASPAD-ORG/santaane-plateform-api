"""
Business logic layer for users module.
Handles validation and orchestration of user operations.
"""
from fastapi import HTTPException, status
from typing import List, Optional
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithRolesResponse,
    UserDetailResponse,
    PasswordChange,
    UserActivation,
    RoleInfo
)
from app.models.user import User
from app.core.security import hash_password, verify_password
from app.core.logging import logger
from app.schemas.base import PaginatedResponse



class UserService:
    """Service for user business logic."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def hard_delete_user(
        self,
        user_id: int,
        current_user: User
    ) -> dict:
        """Hard delete a user (permanent removal)."""
        # Prevent self-deletion
        if user_id == current_user.id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        success = await self.repository.hard_delete(user_id)
        if not success:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return {"message": "User permanently deleted"}

    async def create_user(
        self,
        data: UserCreate,
        current_user: User
    ) -> UserResponse:
        """
        Create a new user.
        Only SUPER_ADMIN can create users.
        """
        # Check if user with email already exists
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{data.email}' already exists"
            )

        # Hash password
        password_hash = hash_password(data.password)

        # Create user
        user = await self.repository.create(data, password_hash)
        return UserResponse.model_validate(user)

    async def get_user(self, user_id: int, current_user: User) -> UserWithRolesResponse:
        """
        Get user by ID with roles.
        Users can view their own profile, SUPER_ADMIN can view any.
        """
        user = await self.repository.get_with_roles(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Convert user_roles to roles list
        roles = []
        if hasattr(user, 'user_roles') and user.user_roles:
            for ur in user.user_roles:
                if hasattr(ur, 'role') and ur.role:
                    roles.append(RoleInfo.model_validate(ur.role))

        # Create response with roles
        user_dict = UserResponse.model_validate(user).model_dump()
        user_dict['roles'] = roles

        return UserWithRolesResponse(**user_dict)

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        country_id: Optional[int] = None
    ) -> PaginatedResponse[UserWithRolesResponse]:
        """List all users with pagination and filtering."""
        users, total = await self.repository.get_all(
            skip=skip,
            limit=limit,
            email=email,
            full_name=full_name,
            role=role,
            is_active=is_active,
            country_id=country_id
        )

        # Convert users with roles
        items = []
        for user in users:
            # Safely extract roles
            roles = []
            if hasattr(user, 'user_roles') and user.user_roles:
                for ur in user.user_roles:
                    if hasattr(ur, 'role') and ur.role:
                        roles.append(RoleInfo.model_validate(ur.role))
            
            user_dict = UserResponse.model_validate(user).model_dump()
            user_dict['roles'] = roles
            items.append(UserWithRolesResponse(**user_dict))

        return PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total
        )

    async def update_user(
        self,
        user_id: int,
        data: UserUpdate,
        current_user: User
    ) -> UserResponse:
        """Update an existing user."""
        # Check if email is being changed and if it conflicts
        if data.email:
            existing = await self.repository.get_by_email(data.email)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with email '{data.email}' already exists"
                )

        user = await self.repository.update(user_id, data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        return UserResponse.model_validate(user)

    async def change_password(
        self,
        user_id: int,
        data: PasswordChange,
        current_user: User
    ) -> dict:
        """Change user password."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Verify current password
        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Hash new password
        new_password_hash = hash_password(data.new_password)

        # Update password
        success = await self.repository.update_password(user_id, new_password_hash)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password"
            )

        return {"message": "Password updated successfully"}

    async def activate_user(
        self,
        user_id: int,
        data: UserActivation,
        current_user: User
    ) -> UserResponse:
        """Activate or deactivate a user."""
        # Prevent self-deactivation
        if user_id == current_user.id and data.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own account."
            )
        user = await self.repository.set_active_status(user_id, data.is_active)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        status_text = "activated" if data.is_active else "deactivated"
        logger.info(f"User {status_text}: {user.email} by {current_user.email}")

        return UserResponse.model_validate(user)

    async def delete_user(
        self,
        user_id: int,
        current_user: User
    ) -> dict:
        """Soft delete a user."""
        # Prevent self-deletion
        if user_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        success = await self.repository.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        return {"message": "User deleted successfully"}
