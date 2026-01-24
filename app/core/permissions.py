"""
Role-Based Access Control (RBAC) dependencies
Provides FastAPI dependencies for protecting routes by user roles
"""
from fastapi import Depends, HTTPException, status
from typing import Callable

from app.core.roles import UserRole
from app.core.security import get_current_user
from app.models.user import User
from app.modules.auth.error_codes import AuthErrorCode
from app.modules.auth.repository import AuthRepository
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger

logger = get_logger(__name__)


def require_role(role: UserRole) -> Callable:
    """
    Dependency to require a specific role.

    Usage:
        @router.post("/publish")
        async def publish(current_user: User = Depends(require_role(UserRole.EDITOR))):
            ...

    Args:
        role: The required role

    Returns:
        FastAPI dependency function

    Raises:
        HTTPException 403: If user doesn't have the required role
        HTTPException 401: If user account is inactive
    """
    async def check_role(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Check if account is active
        if not current_user.is_active:
            logger.warning(f"Inactive account attempted access: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthErrorCode.ACCOUNT_INACTIVE
            )

        # Get user roles
        repository = AuthRepository(db)
        user_roles = await repository.get_user_roles(current_user.id)

        # SUPER_ADMIN has automatic access to everything
        if UserRole.SUPER_ADMIN.value in user_roles:
            logger.info(f"SUPER_ADMIN access granted: {current_user.email}")
            return current_user

        # Check if user has the required role
        if role.value not in user_roles:
            logger.warning(
                f"Insufficient permissions: {current_user.email} "
                f"(has: {user_roles}, needs: {role.value})"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthErrorCode.INSUFFICIENT_PERMISSIONS
            )

        logger.info(f"Role check passed: {current_user.email} has {role.value}")
        return current_user

    return check_role


def require_any_role(*roles: UserRole) -> Callable:
    """
    Dependency to require AT LEAST ONE of the specified roles (OR logic).

    Usage:
        @router.get("/review")
        async def review(
            current_user: User = Depends(require_any_role(UserRole.EDITOR, UserRole.EVALUATOR))
        ):
            ...

    Args:
        *roles: One or more required roles

    Returns:
        FastAPI dependency function

    Raises:
        HTTPException 403: If user doesn't have any of the required roles
        HTTPException 401: If user account is inactive
        HTTPException 400: If no roles are specified
    """
    if not roles:
        raise ValueError("At least one role must be specified")

    async def check_any_role(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Check if account is active
        if not current_user.is_active:
            logger.warning(f"Inactive account attempted access: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthErrorCode.ACCOUNT_INACTIVE
            )

        # Get user roles
        repository = AuthRepository(db)
        user_roles = await repository.get_user_roles(current_user.id)

        # SUPER_ADMIN has automatic access to everything
        if UserRole.SUPER_ADMIN.value in user_roles:
            logger.info(f"SUPER_ADMIN access granted: {current_user.email}")
            return current_user

        # Check if user has at least one of the required roles
        required_role_values = [r.value for r in roles]
        has_required_role = any(role in user_roles for role in required_role_values)

        if not has_required_role:
            logger.warning(
                f"Insufficient permissions: {current_user.email} "
                f"(has: {user_roles}, needs any of: {required_role_values})"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthErrorCode.INSUFFICIENT_PERMISSIONS
            )

        logger.info(
            f"Role check passed: {current_user.email} has one of {required_role_values}"
        )
        return current_user

    return check_any_role


def require_all_roles(*roles: UserRole) -> Callable:
    """
    Dependency to require ALL of the specified roles (AND logic).

    Usage:
        @router.delete("/admin-action")
        async def admin_action(
            current_user: User = Depends(require_all_roles(UserRole.SUPER_ADMIN, UserRole.EDITOR))
        ):
            ...

    Args:
        *roles: All required roles

    Returns:
        FastAPI dependency function

    Raises:
        HTTPException 403: If user doesn't have all required roles
        HTTPException 401: If user account is inactive
        HTTPException 400: If no roles are specified
    """
    if not roles:
        raise ValueError("At least one role must be specified")

    async def check_all_roles(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Check if account is active
        if not current_user.is_active:
            logger.warning(f"Inactive account attempted access: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthErrorCode.ACCOUNT_INACTIVE
            )

        # Get user roles
        repository = AuthRepository(db)
        user_roles = await repository.get_user_roles(current_user.id)

        # SUPER_ADMIN has automatic access to everything
        if UserRole.SUPER_ADMIN.value in user_roles:
            logger.info(f"SUPER_ADMIN access granted: {current_user.email}")
            return current_user

        # Check if user has ALL required roles
        required_role_values = [r.value for r in roles]
        has_all_roles = all(role in user_roles for role in required_role_values)

        if not has_all_roles:
            missing_roles = [r for r in required_role_values if r not in user_roles]
            logger.warning(
                f"Insufficient permissions: {current_user.email} "
                f"(has: {user_roles}, needs all of: {required_role_values}, missing: {missing_roles})"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AuthErrorCode.INSUFFICIENT_PERMISSIONS
            )

        logger.info(
            f"Role check passed: {current_user.email} has all of {required_role_values}"
        )
        return current_user

    return check_all_roles


def require_editor_or_manuscript_author(manuscript_id: int) -> Callable:
    """
    Dependency to require EDITOR role OR manuscript ownership (AUTHOR).

    Usage:
        @router.get("/{manuscript_id}/evaluations")
        async def get_evaluations(
            manuscript_id: int,
            current_user: User = Depends(require_editor_or_manuscript_author(manuscript_id))
        ):
            ...

    Args:
        manuscript_id: ID of the manuscript to check ownership

    Returns:
        FastAPI dependency function

    Raises:
        HTTPException 403: If user is neither EDITOR nor manuscript owner
        HTTPException 401: If user account is inactive
        HTTPException 404: If manuscript not found
    """
    async def check_editor_or_owner(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Check if account is active
        if not current_user.is_active:
            logger.warning(f"Inactive account attempted access: {current_user.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AuthErrorCode.ACCOUNT_INACTIVE
            )

        # Get user roles
        repository = AuthRepository(db)
        user_roles = await repository.get_user_roles(current_user.id)

        # SUPER_ADMIN has automatic access
        if UserRole.SUPER_ADMIN.value in user_roles:
            logger.info(f"SUPER_ADMIN access granted: {current_user.email}")
            return current_user

        # EDITOR has automatic access
        if UserRole.EDITOR.value in user_roles:
            logger.info(f"EDITOR access granted: {current_user.email}")
            return current_user

        # Check if user is AUTHOR and owns the manuscript
        if UserRole.AUTHOR.value in user_roles:
            from app.models.manuscript import Manuscript
            from sqlmodel import select

            # Query manuscript to check ownership
            query = select(Manuscript).where(Manuscript.id == manuscript_id)
            result = await db.execute(query)
            manuscript = result.scalar_one_or_none()

            if not manuscript:
                logger.warning(f"Manuscript {manuscript_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Manuscript not found"
                )

            if manuscript.author_id == current_user.id:
                logger.info(f"AUTHOR access granted (owns manuscript {manuscript_id}): {current_user.email}")
                return current_user

        # User is neither EDITOR nor manuscript owner
        logger.warning(
            f"Insufficient permissions: {current_user.email} "
            f"(has: {user_roles}, needs: EDITOR or manuscript ownership)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=AuthErrorCode.INSUFFICIENT_PERMISSIONS
        )

    return check_editor_or_owner


# Convenience aliases for common role checks
require_super_admin = require_role(UserRole.SUPER_ADMIN)
require_editor = require_role(UserRole.EDITOR)
require_evaluator = require_role(UserRole.EVALUATOR)
require_mentor = require_role(UserRole.MENTOR)
require_author = require_role(UserRole.AUTHOR)
