"""
assign_auteur_mentor module - API routes for Mentor Assignment
"""
from fastapi import APIRouter, Depends, Query, status, HTTPException

from app.core.security import get_current_user
from app.core.permissions import require_any_role
from app.core.roles import UserRole
from app.models.user import User
from app.modules.assign_auteur_mentor.schemas import (
    MentorAssignmentCreate,
    MentorAssignmentUpdate,
    MentorAssignmentResponse,
    PaginatedMentorAssignmentResponse,
    SuccessMessageResponse
)
from app.modules.assign_auteur_mentor.service import MentorAssignmentService
from app.modules.assign_auteur_mentor.utils import get_mentor_assignment_service
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/mentors", tags=["Mentor Assignment"])


@router.post(
    "/assign",
    response_model=MentorAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign an author to a mentor",
    description="Create a new mentor assignment. Only SUPER_ADMIN or EDITOR can perform this action."
)
async def create_mentor_assignment(
    assignment_data: MentorAssignmentCreate,
    current_user: User = Depends(require_any_role(UserRole.SUPER_ADMIN, UserRole.EDITOR)),
    service: MentorAssignmentService = Depends(get_mentor_assignment_service)
):
    """
    Assign an Author to a Mentor.
    
    - **author_id**: ID of the author to be assigned (must have AUTHOR role)
    - **mentor_id**: ID of the mentor to assign (must have MENTOR role)
    
    Business rules:
    - Author and mentor must be different users
    - Author must have the AUTHOR role
    - Mentor must have the MENTOR role
    - An author can only have one active mentor at a time
    - Previous active assignments are automatically deactivated
    
    Only users with SUPER_ADMIN or EDITOR roles can create assignments.
    """
    return await service.create_assignment(assignment_data, current_user)


@router.put(
    "/assign/{assignment_id}",
    response_model=MentorAssignmentResponse,
    summary="Update a mentor assignment",
    description="Modify an existing mentor assignment. Only SUPER_ADMIN or EDITOR can perform this action."
)
async def update_mentor_assignment(
    assignment_id: int,
    update_data: MentorAssignmentUpdate,
    current_user: User = Depends(require_any_role(UserRole.SUPER_ADMIN, UserRole.EDITOR)),
    service: MentorAssignmentService = Depends(get_mentor_assignment_service)
):
    """
    Update a Mentor Assignment.
    
    - **assignment_id**: ID of the assignment to update
    - **mentor_id** (optional): Change the mentor for this assignment
    - **is_active** (optional): Change the active status
    
    Business rules:
    - New mentor must have MENTOR role
    - If setting is_active to true, previous active assignments are deactivated
    - Author cannot be the same as mentor
    
    Only users with SUPER_ADMIN or EDITOR roles can update assignments.
    """
    return await service.update_assignment(assignment_id, update_data, current_user)


@router.delete(
    "/assign/{assignment_id}",
    response_model=SuccessMessageResponse,
    summary="Delete a mentor assignment",
    description="Remove a mentor assignment. Only SUPER_ADMIN or EDITOR can perform this action."
)
async def delete_mentor_assignment(
    assignment_id: int,
    current_user: User = Depends(require_any_role(UserRole.SUPER_ADMIN, UserRole.EDITOR)),
    service: MentorAssignmentService = Depends(get_mentor_assignment_service)
):
    """
    Delete a Mentor Assignment.
    
    - **assignment_id**: ID of the assignment to delete
    
    This will permanently remove the mentor assignment. The author will no longer have an active mentor.
    
    Only users with SUPER_ADMIN or EDITOR roles can delete assignments.
    """
    return await service.delete_assignment(assignment_id, current_user)


@router.get(
    "/assign/{assignment_id}",
    response_model=MentorAssignmentResponse,
    summary="Get a mentor assignment by ID",
    description="Retrieve details of a specific mentor assignment."
)
async def get_mentor_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    service: MentorAssignmentService = Depends(get_mentor_assignment_service)
):
    """
    Get a Mentor Assignment by ID.
    
    - **assignment_id**: ID of the assignment to retrieve
    
    Returns the mentor assignment details including author, mentor, and who created the assignment.
    """
    return await service.get_assignment_by_id(assignment_id)


@router.get(
    "/assign",
    response_model=PaginatedMentorAssignmentResponse,
    summary="List all mentor assignments",
    description="Retrieve a paginated list of all mentor assignments."
)
async def list_mentor_assignments(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    current_user: User = Depends(get_current_user),
    service: MentorAssignmentService = Depends(get_mentor_assignment_service)
):
    """
    List all Mentor Assignments with pagination.
    
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Number of items to return (max 100)
    
    Returns a paginated list of all mentor assignments in the system.
    """
    return await service.get_all_assignments(skip=skip, limit=limit)


@router.get(
    "/{mentor_id}/authors",
    response_model=PaginatedMentorAssignmentResponse,
    summary="Get all authors assigned to a mentor",
    description="Retrieve all authors currently mentored by a specific mentor."
)
async def get_mentor_authors(
    mentor_id: int,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    active_only: bool = Query(True, description="Only return active assignments"),
    current_user: User = Depends(get_current_user),
    service: MentorAssignmentService = Depends(get_mentor_assignment_service)
):
    """
    Get all Authors assigned to a Mentor.
    
    - **mentor_id**: ID of the mentor
    - **skip**: Number of items to skip (for pagination)
    - **limit**: Number of items to return (max 100)
    - **active_only**: If true, only return active assignments (default: true)
    
    Returns a paginated list of authors assigned to the specified mentor.
    
    Permission rules:
    - SUPER_ADMIN and EDITOR can view any mentor's authors
    - Mentors can view their own authors
    - Others get a 403 Forbidden error
    """
    return await service.get_mentor_authors(
        mentor_id=mentor_id,
        current_user=current_user,
        skip=skip,
        limit=limit,
        active_only=active_only
    )
