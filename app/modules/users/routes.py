"""
API routes for users module.
All endpoints require appropriate role-based permissions.
"""
from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from app.modules.users.service import UserService
from app.modules.users.utils import get_user_service
from app.modules.users.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithRolesResponse,
    PasswordChange,
    UserActivation
)
from app.core.permissions import require_super_admin, get_current_user, require_any_role
from app.models.user import User
from app.core.roles import UserRole
from app.schemas.base import PaginatedResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    dependencies=[Depends(require_super_admin)]
)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Create a new user.

    **Requires:** SUPER_ADMIN role

    **Parameters:**
    - **email**: Unique email address
    - **password**: Password (min 8 chars, must contain uppercase, lowercase, and digit)
    - **fullName**: User's full name
    - **countryId**: Optional country ID
    - **cityId**: Optional city ID
    - **timezone**: Optional timezone
    - **orcidId**: Optional ORCID identifier
    """
    return await service.create_user(data, current_user)


@router.get(
    "",
    response_model=PaginatedResponse[UserWithRolesResponse],
    summary="List all users",
    dependencies=[Depends(require_super_admin)]
)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    email: Optional[str] = Query(None, description="Filter by email (partial match)"),
    full_name: Optional[str] = Query(None, description="Filter by name (partial match)", alias="fullName"),
    role: Optional[str] = Query(None, description="Filter by role name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status", alias="isActive"),
    country_id: Optional[int] = Query(None, description="Filter by country", alias="countryId"),
    service: UserService = Depends(get_user_service)
):
    """
    List all users with pagination and filtering.

    **Requires:** SUPER_ADMIN role

    **Parameters:**
    - **skip**: Number of records to skip (pagination offset)
    - **limit**: Maximum number of records to return (page size)
    - **email**: Optional filter by email (partial match)
    - **fullName**: Optional filter by name (partial match)
    - **role**: Optional filter by role name
    - **isActive**: Optional filter by active status
    - **countryId**: Optional filter by country
    """
    return await service.list_users(
        skip=skip,
        limit=limit,
        email=email,
        full_name=full_name,
        role=role,
        is_active=is_active,
        country_id=country_id
    )


@router.get(
    "/{user_id}",
    response_model=UserWithRolesResponse,
    summary="Get user details"
)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Get detailed information about a specific user.

    **Requires:** Authentication (users can view their own profile, SUPER_ADMIN can view any)

    **Parameters:**
    - **user_id**: ID of the user
    """
    # Check permission: can view own profile or must be SUPER_ADMIN
    if user_id != current_user.id:
        # Will be checked by permission dependency if needed
        pass

    return await service.get_user(user_id, current_user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
    dependencies=[Depends(require_super_admin)]
)
async def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Update an existing user.

    **Requires:** SUPER_ADMIN role

    **Parameters:**
    - **user_id**: ID of the user to update
    - **email**: Optional new email
    - **fullName**: Optional new full name
    - **countryId**: Optional new country ID
    - **cityId**: Optional new city ID
    - **timezone**: Optional new timezone
    - **profilePhoto**: Optional new profile photo URL
    - **orcidId**: Optional new ORCID identifier
    """
    return await service.update_user(user_id, data, current_user)


@router.put(
    "/{user_id}/password",
    summary="Change user password"
)
async def change_password(
    user_id: int,
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Change user password.

    **Requires:** Authentication (users can only change their own password)

    **Parameters:**
    - **user_id**: ID of the user
    - **currentPassword**: Current password
    - **newPassword**: New password (min 8 chars, must contain uppercase, lowercase, and digit)
    """
    # Only allow users to change their own password
    if user_id != current_user.id:
        # Check if SUPER_ADMIN
        from app.modules.users.repository import UserRepository
        from app.db import get_db

        async for db in get_db():
            repo = UserRepository(db)
            is_super_admin = await repo.has_role(current_user.id, "SUPER_ADMIN")
            if not is_super_admin:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only change your own password"
                )

    return await service.change_password(user_id, data, current_user)


@router.post(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate or deactivate a user",
    dependencies=[Depends(require_super_admin)]
)
async def activate_user(
    user_id: int,
    data: UserActivation,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Activate or deactivate a user account.

    **Requires:** SUPER_ADMIN role

    **Parameters:**
    - **user_id**: ID of the user
    - **isActive**: True to activate, False to deactivate
    """
    return await service.activate_user(user_id, data, current_user)


@router.delete(
    "/{user_id}",
    summary="Delete a user",
    dependencies=[Depends(require_super_admin)]
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    """
    Soft delete a user (sets isActive to false).

    **Requires:** SUPER_ADMIN role

    **Note:** Users cannot delete their own account.

    **Parameters:**
    - **user_id**: ID of the user to delete
    """
    return await service.delete_user(user_id, current_user)
