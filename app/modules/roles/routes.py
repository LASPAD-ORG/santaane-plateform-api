"""
roles module - API routes
Handles HTTP endpoints for roles management
"""
from fastapi import APIRouter, Depends, Query, status

from app.core.security import get_current_user
from app.core.permissions import (
    require_role, require_any_role, require_all_roles,
    require_super_admin, require_editor, require_author
)
from app.core.roles import UserRole
from app.models.user import User
from app.modules.roles.schemas import (
    RoleCreate, RoleUpdate, RoleResponse, PaginatedRoleResponse,
    UserRoleAssign, UserRoleResponse
)
from app.modules.roles.service import RoleService
from app.modules.roles.utils import get_role_service

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=PaginatedRoleResponse)
async def get_all_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """
    Get all roles with pagination
    Requires authentication
    """
    return await service.get_all_roles(skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """
    Get a specific role by ID
    Requires authentication
    """
    return await service.get_role_by_id(role_id)


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """
    Create a new role
    Requires authentication
    """
    return await service.create_role(role_data)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """
    Update an existing role
    Requires authentication
    """
    return await service.update_role(role_id, role_data)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """
    Delete a role
    Requires authentication
    """
    await service.delete_role(role_id)


# User roles management endpoints
@router.post("/assign", response_model=UserRoleResponse, status_code=status.HTTP_201_CREATED)
async def assign_role(
    assign_data: UserRoleAssign,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """
    Assign a role to a user
    Requires authentication
    The current user will be recorded as the assigner
    """
    return await service.assign_role_to_user(assign_data, assigned_by=current_user.id)


@router.delete("/remove/{user_id}/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_role(
    user_id: int,
    role_id: int,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """
    Remove a role from a user
    Requires authentication
    """
    await service.remove_role_from_user(user_id, role_id)


@router.get("/user/{user_id}", response_model=list[UserRoleResponse])
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: RoleService = Depends(get_role_service)
):
    """
    Get all roles for a specific user
    Requires authentication
    """
    return await service.get_user_roles(user_id)


# RBAC Demo/Test Endpoints
@router.get("/test/super-admin-only")
async def test_super_admin_only(current_user: User = Depends(require_super_admin)):
    """
    Test endpoint - Only SUPER_ADMIN can access
    """
    return {
        "message": "Success! You are a SUPER_ADMIN",
        "user": current_user.email,
        "access_level": "SUPER_ADMIN"
    }


@router.get("/test/editor-only")
async def test_editor_only(current_user: User = Depends(require_editor)):
    """
    Test endpoint - Only EDITOR (or SUPER_ADMIN) can access
    """
    return {
        "message": "Success! You are an EDITOR",
        "user": current_user.email,
        "access_level": "EDITOR"
    }


@router.get("/test/editor-or-evaluator")
async def test_editor_or_evaluator(
    current_user: User = Depends(require_any_role(UserRole.EDITOR, UserRole.EVALUATOR))
):
    """
    Test endpoint - EDITOR OR EVALUATOR can access (OR logic)
    """
    return {
        "message": "Success! You are EDITOR or EVALUATOR",
        "user": current_user.email,
        "access_level": "EDITOR or EVALUATOR"
    }


@router.get("/test/editor-and-mentor")
async def test_editor_and_mentor(
    current_user: User = Depends(require_all_roles(UserRole.EDITOR, UserRole.MENTOR))
):
    """
    Test endpoint - Must have BOTH EDITOR AND MENTOR roles (AND logic)
    """
    return {
        "message": "Success! You have both EDITOR and MENTOR roles",
        "user": current_user.email,
        "access_level": "EDITOR + MENTOR"
    }
