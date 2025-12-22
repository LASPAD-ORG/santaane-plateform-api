"""
Theme service - Business logic for theme operations
"""
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.models.theme import Theme
from app.modules.themes.schemas import ThemeCreate, ThemeUpdate


class ThemeService:
    """Service class for theme operations"""

    @staticmethod
    async def create_theme(db: AsyncSession, theme_data: ThemeCreate) -> Theme:
        """Create a new theme"""
        theme = Theme(
            title=theme_data.title,
            description=theme_data.description,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(theme)
        await db.commit()
        await db.refresh(theme)
        return theme

    @staticmethod
    async def get_theme(db: AsyncSession, theme_id: int) -> Optional[Theme]:
        """Get a theme by ID"""
        result = await db.execute(select(Theme).where(Theme.id == theme_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_themes(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Theme]:
        """Get all themes with pagination"""
        result = await db.execute(select(Theme).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_theme(db: AsyncSession, theme_id: int, theme_data: ThemeUpdate) -> Optional[Theme]:
        """Update a theme"""
        theme = await ThemeService.get_theme(db, theme_id)
        if not theme:
            return None

        update_data = theme_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(theme, field, value)
        
        theme.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(theme)
        return theme

    @staticmethod
    async def delete_theme(db: AsyncSession, theme_id: int) -> bool:
        """Delete a theme"""
        theme = await ThemeService.get_theme(db, theme_id)
        if not theme:
            return False

        await db.delete(theme)
        await db.commit()
        return True
