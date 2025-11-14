"""
API routes for laboratories module.
All endpoints require appropriate role-based permissions.
"""
from fastapi import APIRouter, Depends, Query, status
from typing import Optional, List
from app.modules.laboratories.service import LaboratoryService
from app.modules.laboratories.utils import get_laboratory_service
from app.modules.laboratories.schemas import (
    LaboratoryCreate,
    LaboratoryUpdate,
    LaboratoryResponse,
    LaboratoryWithEditorsResponse,
    EditorAssignmentCreate,
    EditorAssignmentResponse,
    AvailableEditorResponse
)
from app.core.permissions import require_super_admin, get_current_user
from app.models.user import User
from app.schemas.base import PaginatedResponse


router = APIRouter(prefix="/laboratories", tags=["Laboratories"])


@router.post(
    "",
    response_model=LaboratoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new laboratory",
    dependencies=[Depends(require_super_admin)]
)
async def create_laboratory(
    data: LaboratoryCreate,
    current_user: User = Depends(get_current_user),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Create a new laboratory.

    **Requires:** SUPER_ADMIN role

    **Parameters:**
    - **name**: Unique laboratory name
    - **description**: Optional description
    - **isActive**: Whether laboratory is active (default: true)
    """
    return await service.create_laboratory(data, current_user)


@router.get(
    "",
    response_model=PaginatedResponse[LaboratoryResponse],
    summary="List all laboratories"
)
async def list_laboratories(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    List all laboratories with pagination.

    **Parameters:**
    - **skip**: Number of records to skip (pagination offset)
    - **limit**: Maximum number of records to return (page size)
    - **isActive**: Optional filter by active status
    """
    return await service.list_laboratories(skip=skip, limit=limit, is_active=is_active)


@router.get(
    "/available-editors",
    response_model=List[AvailableEditorResponse],
    summary="Get available editors for assignment",
    dependencies=[Depends(require_super_admin)]
)
async def get_available_editors(
    laboratory_id: Optional[int] = Query(None, description="Exclude editors already assigned to this lab"),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Get all users with EDITOR role available for laboratory assignment.

    **Requires:** SUPER_ADMIN role

    **Parameters:**
    - **laboratory_id**: Optional - if provided, excludes editors already assigned to this lab
    """
    return await service.get_available_editors(laboratory_id)


@router.get(
    "/{laboratory_id}",
    response_model=LaboratoryResponse,
    summary="Get laboratory details"
)
async def get_laboratory(
    laboratory_id: int,
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Get detailed information about a specific laboratory.

    **Parameters:**
    - **laboratory_id**: ID of the laboratory
    """
    return await service.get_laboratory(laboratory_id)


@router.put(
    "/{laboratory_id}",
    response_model=LaboratoryResponse,
    summary="Update a laboratory",
    dependencies=[Depends(require_super_admin)]
)
async def update_laboratory(
    laboratory_id: int,
    data: LaboratoryUpdate,
    current_user: User = Depends(get_current_user),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Update an existing laboratory.

    **Requires:** SUPER_ADMIN role

    **Parameters:**
    - **laboratory_id**: ID of the laboratory to update
    - **name**: Optional new name
    - **description**: Optional new description
    - **isActive**: Optional active status update
    """
    return await service.update_laboratory(laboratory_id, data, current_user)


@router.delete(
    "/{laboratory_id}",
    summary="Delete a laboratory",
    dependencies=[Depends(require_super_admin)]
)
async def delete_laboratory(
    laboratory_id: int,
    current_user: User = Depends(get_current_user),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Soft delete a laboratory (sets isActive to false).

    **Requires:** SUPER_ADMIN role

    **Note:** LASPAD laboratory cannot be deleted.

    **Parameters:**
    - **laboratory_id**: ID of the laboratory to delete
    """
    return await service.delete_laboratory(laboratory_id, current_user)


# Editor Assignment Endpoints

@router.post(
    "/{laboratory_id}/editors",
    response_model=EditorAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign an editor to a laboratory",
    dependencies=[Depends(require_super_admin)]
)
async def assign_editor_to_laboratory(
    laboratory_id: int,
    data: EditorAssignmentCreate,
    current_user: User = Depends(get_current_user),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Assign an editor to a laboratory.

    **Requires:** SUPER_ADMIN role

    **Parameters:**
    - **laboratory_id**: ID of the laboratory
    - **userId**: ID of the user (must have EDITOR role)
    - **role**: Editorial role (chief_editor, associate_editor, etc.)
    """
    return await service.assign_editor(laboratory_id, data, current_user)


@router.delete(
    "/{laboratory_id}/editors/{user_id}",
    summary="Remove an editor from a laboratory",
    dependencies=[Depends(require_super_admin)]
)
async def unassign_editor_from_laboratory(
    laboratory_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Remove an editor from a laboratory (soft delete).

    **Requires:** SUPER_ADMIN role

    **Parameters:**
    - **laboratory_id**: ID of the laboratory
    - **user_id**: ID of the editor to remove
    """
    return await service.unassign_editor(laboratory_id, user_id, current_user)


@router.get(
    "/{laboratory_id}/editors",
    response_model=List[EditorAssignmentResponse],
    summary="Get laboratory editors"
)
async def get_laboratory_editors(
    laboratory_id: int,
    service: LaboratoryService = Depends(get_laboratory_service)
):
    """
    Get all editors assigned to a laboratory.

    **Parameters:**
    - **laboratory_id**: ID of the laboratory
    """
    return await service.get_laboratory_editors(laboratory_id)
