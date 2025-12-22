"""
Theme router - API endpoints for theme management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import get_db
from app.core.security import get_current_user
from app.core.permissions import require_role
from app.core.roles import UserRole
from app.models.user import User
from app.modules.themes.schemas import ThemeCreate, ThemeUpdate, ThemeResponse
from app.modules.themes.service import ThemeService

router = APIRouter(prefix="/themes", tags=["Themes"])


@router.post(
    "/",
    response_model=ThemeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new theme",
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)
async def create_theme(
    theme_data: ThemeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new theme (SUPER_ADMIN only)
    """
    theme = await ThemeService.create_theme(db, theme_data)
    return theme


@router.get(
    "/",
    response_model=List[ThemeResponse],
    summary="Get all themes"
)
async def get_themes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all themes with pagination
    """
    themes = await ThemeService.get_all_themes(db, skip, limit)
    return themes


@router.get(
    "/{theme_id}",
    response_model=ThemeResponse,
    summary="Get a theme by ID"
)
async def get_theme(
    theme_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific theme by ID
    """
    theme = await ThemeService.get_theme(db, theme_id)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    return theme


@router.put(
    "/{theme_id}",
    response_model=ThemeResponse,
    summary="Update a theme",
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)
async def update_theme(
    theme_id: int,
    theme_data: ThemeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a theme (SUPER_ADMIN only)
    """
    theme = await ThemeService.update_theme(db, theme_id, theme_data)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    return theme


@router.delete(
    "/{theme_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a theme",
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)
async def delete_theme(
    theme_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a theme (SUPER_ADMIN only)
    """
    deleted = await ThemeService.delete_theme(db, theme_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
