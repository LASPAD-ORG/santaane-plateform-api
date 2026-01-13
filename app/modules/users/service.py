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
    ProfileUpdate,
    UserResponse,
    UserWithRolesResponse,
    UserDetailResponse,
    PasswordChange,
    AdminPasswordReset,
    UserActivation,
    RoleInfo,
    EvaluatorCreate
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
        
        # Send new user credentials email
        from app.core.email import EmailService
        
        # Get user with roles loaded
        user_with_roles = await self.repository.get_with_roles(user.id)
        
        # Get the first role name if available, otherwise use 'User' as default
        role_name = 'User'
        if user_with_roles and user_with_roles.user_roles:
            # Get the first role's name if available
            first_role = user_with_roles.user_roles[0]
            if hasattr(first_role, 'role') and hasattr(first_role.role, 'name'):
                role_name = first_role.role.name
        
        # Send email in background task to avoid blocking
        EmailService.send_new_user_credentials(
            to_email=user.email,
            full_name=user.full_name,
            password=data.password,  # Use the plain password before hashing
            role=role_name
        )
        
        return UserResponse.model_validate(user)

    async def create_evaluator(
        self,
        data: EvaluatorCreate,
        current_user: User
    ) -> UserWithRolesResponse:
        """
        Create a new evaluator account.
        Only EDITOR and SUPER_ADMIN can create evaluators.
        Generates a random password and sends it via email.
        """
        import secrets
        import string
        from app.core.email import EmailService
        
        # Check if user with email already exists
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{data.email}' already exists"
            )

        # Generate random password (12 characters: letters, digits, and special chars)
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Hash password
        password_hash = hash_password(password)

        # Create user with additional fields
        from app.models.user import User as UserModel
        user_data = UserModel(
            email=data.email,
            email_verified=False,
            password_hash=password_hash,
            full_name=data.full_name,
            orcid_id=data.orcid_id,
            bio=data.bio,
            position=data.position,
            institution=data.institution,
            is_active=True
        )
        
        user = await self.repository.create_user_model(user_data)
        
        # Assign EVALUATOR role (role_id = 3)
        await self.repository.assign_role(user.id, 3, current_user.id)
        
        # Send welcome email with credentials
        email_sent = EmailService.send_welcome_email(
            to_email=data.email,
            full_name=data.full_name,
            password=password,
            role="EVALUATOR"
        )
        
        if not email_sent:
            logger.warning(f"Failed to send welcome email to {data.email}")
        
        # Get user with roles
        user_with_roles = await self.repository.get_with_roles(user.id)
        
        # Convert to response
        roles = []
        if hasattr(user_with_roles, 'user_roles') and user_with_roles.user_roles:
            for ur in user_with_roles.user_roles:
                if hasattr(ur, 'role') and ur.role:
                    roles.append(RoleInfo.model_validate(ur.role))
        
        user_dict = UserResponse.model_validate(user_with_roles).model_dump()
        user_dict['roles'] = roles
        
        return UserWithRolesResponse(**user_dict)

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

    async def list_evaluators(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> PaginatedResponse[UserWithRolesResponse]:
        """List all evaluators with pagination."""
        evaluators, total = await self.repository.get_all_evaluators(
            skip=skip,
            limit=limit
        )

        # Convert evaluators with roles
        items = []
        for evaluator in evaluators:
            # Safely extract roles
            roles = []
            if hasattr(evaluator, 'user_roles') and evaluator.user_roles:
                for ur in evaluator.user_roles:
                    if hasattr(ur, 'role') and ur.role:
                        roles.append(RoleInfo.model_validate(ur.role))

            # Create user response
            user_dict = UserResponse.model_validate(evaluator).model_dump()
            user_dict['roles'] = roles

            items.append(UserWithRolesResponse(**user_dict))

        return PaginatedResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + limit) < total
        )

    async def list_users(
        self,
        skip: int = 0,
        limit: int = 20,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> PaginatedResponse[UserWithRolesResponse]:
        """List all users with pagination and filtering."""
        users, total = await self.repository.get_all(
            skip=skip,
            limit=limit,
            email=email,
            full_name=full_name,
            role=role,
            is_active=is_active
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

    async def update_own_profile(
        self,
        user_id: int,
        data: ProfileUpdate
    ) -> UserResponse:
        """Update own profile (users cannot change email)."""
        # Get user first
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Update all fields manually
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.profile_photo is not None:
            user.profile_photo = data.profile_photo
        if data.orcid_id is not None:
            user.orcid_id = data.orcid_id
        if data.bio is not None:
            user.bio = data.bio
        if data.position is not None:
            user.position = data.position
        if data.institution is not None:
            user.institution = data.institution
        
        # Commit changes
        await self.repository.db.commit()
        await self.repository.db.refresh(user)

        logger.info(f"Profile updated for user: {user.email} (ID: {user.id})")
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

    async def reset_user_password(
        self,
        user_id: int,
        data: AdminPasswordReset,
        current_user: User
    ) -> dict:
        """
        Reset user password (admin only).
        Admin does not need to know current password.
        """
        # Get target user
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )

        # Hash new password
        new_password_hash = hash_password(data.new_password)

        # Update password
        success = await self.repository.update_password(user_id, new_password_hash)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset password"
            )

        logger.info(f"Admin {current_user.id} reset password for user {user_id}")
        return {"message": "Password reset successfully"}

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
