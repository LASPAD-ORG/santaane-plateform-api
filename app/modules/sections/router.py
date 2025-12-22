"""
Section router - API endpoints for section management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import get_db
from app.core.security import get_current_user
from app.core.permissions import require_role
from app.core.roles import UserRole
from app.models.user import User
from app.modules.sections.schemas import SectionCreate, SectionUpdate, SectionResponse
from app.modules.sections.service import SectionService

router = APIRouter(prefix="/sections", tags=["Sections"])


@router.post(
    "/",
    response_model=SectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new section",
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)
async def create_section(
    section_data: SectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new section (SUPER_ADMIN only)
    """
    section = await SectionService.create_section(db, section_data)
    return section


@router.get(
    "/",
    response_model=List[SectionResponse],
    summary="Get all sections"
)
async def get_sections(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all sections with pagination
    """
    sections = await SectionService.get_all_sections(db, skip, limit)
    return sections


@router.get(
    "/{section_id}",
    response_model=SectionResponse,
    summary="Get a section by ID"
)
async def get_section(
    section_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific section by ID
    """
    section = await SectionService.get_section(db, section_id)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    return section


@router.put(
    "/{section_id}",
    response_model=SectionResponse,
    summary="Update a section",
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)
async def update_section(
    section_id: int,
    section_data: SectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a section (SUPER_ADMIN only)
    """
    try:
        section = await SectionService.update_section(db, section_id, section_data)
        if not section:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Section not found"
            )
        return section
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a section",
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)
async def delete_section(
    section_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a section (SUPER_ADMIN only)
    """
    deleted = await SectionService.delete_section(db, section_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
