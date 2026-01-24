"""
Language router - API endpoints for language management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import get_db
from app.core.security import get_current_user
from app.core.permissions import require_role
from app.core.roles import UserRole
from app.models.user import User
from app.modules.languages.schemas import LanguageCreate, LanguageUpdate, LanguageResponse
from app.modules.languages.service import LanguageService

router = APIRouter(prefix="/languages", tags=["Languages"])


@router.post(
    "/",
    response_model=LanguageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new language",
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)
async def create_language(
    language_data: LanguageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new language (SUPER_ADMIN only)
    """
    language = await LanguageService.create_language(db, language_data)
    return language


@router.get(
    "/",
    response_model=List[LanguageResponse],
    summary="Get all languages"
)
async def get_languages(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all languages with pagination
    """
    languages = await LanguageService.get_all_languages(db, skip, limit)
    return languages


@router.get(
    "/{language_id}",
    response_model=LanguageResponse,
    summary="Get a language by ID"
)
async def get_language(
    language_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a specific language by ID
    """
    language = await LanguageService.get_language(db, language_id)
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Language not found"
        )
    return language


@router.put(
    "/{language_id}",
    response_model=LanguageResponse,
    summary="Update a language",
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)
async def update_language(
    language_id: int,
    language_data: LanguageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a language (SUPER_ADMIN only)
    """
    language = await LanguageService.update_language(db, language_id, language_data)
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Language not found"
        )
    return language


@router.delete(
    "/{language_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a language",
    dependencies=[Depends(require_role(UserRole.SUPER_ADMIN))]
)
async def delete_language(
    language_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a language (SUPER_ADMIN only)
    """
    deleted = await LanguageService.delete_language(db, language_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Language not found"
        )
