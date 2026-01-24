"""
Language service - Business logic for language operations
"""
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.models.language import Language
from app.modules.languages.schemas import LanguageCreate, LanguageUpdate


class LanguageService:
    """Service class for language operations"""

    @staticmethod
    async def create_language(db: AsyncSession, language_data: LanguageCreate) -> Language:
        """Create a new language"""
        language = Language(
            name=language_data.name,
            code=language_data.code,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(language)
        await db.commit()
        await db.refresh(language)
        return language

    @staticmethod
    async def get_language(db: AsyncSession, language_id: int) -> Optional[Language]:
        """Get a language by ID"""
        result = await db.execute(select(Language).where(Language.id == language_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_languages(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Language]:
        """Get all languages with pagination"""
        result = await db.execute(select(Language).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_language(db: AsyncSession, language_id: int, language_data: LanguageUpdate) -> Optional[Language]:
        """Update a language"""
        language = await LanguageService.get_language(db, language_id)
        if not language:
            return None

        update_data = language_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(language, field, value)
        
        language.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(language)
        return language

    @staticmethod
    async def delete_language(db: AsyncSession, language_id: int) -> bool:
        """Delete a language"""
        language = await LanguageService.get_language(db, language_id)
        if not language:
            return False

        await db.delete(language)
        await db.commit()
        return True
