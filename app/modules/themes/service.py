"""
Theme service - Business logic for theme operations
"""
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, timezone

from app.models.theme import Theme
from app.modules.themes.schemas import ThemeCreate, ThemeUpdate


class ThemeService:
    """Service class for theme operations"""

    @staticmethod
    async def create_theme(db: AsyncSession, theme_data: ThemeCreate) -> Theme:
        """Create a new theme"""
        # Convert date_limite to naive UTC if it has timezone info
        date_limite_naive = None
        if theme_data.date_limite:
            if theme_data.date_limite.tzinfo is not None:
                date_limite_naive = theme_data.date_limite.astimezone(timezone.utc).replace(tzinfo=None)
            else:
                date_limite_naive = theme_data.date_limite
        
        current_time_naive = datetime.now(timezone.utc).replace(tzinfo=None)
        
        theme = Theme(
            title=theme_data.title,
            description=theme_data.description,
            date_limite=date_limite_naive,
            created_at=current_time_naive,
            updated_at=current_time_naive
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
    async def get_active_themes(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Theme]:
        """Get all active themes (not expired) with pagination"""
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        query = select(Theme).where(
            (Theme.date_limite.is_(None)) | 
            (Theme.date_limite > current_time)
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_expired_themes(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Theme]:
        """Get all expired themes with pagination"""
        current_time = datetime.now(timezone.utc).replace(tzinfo=None)
        query = select(Theme).where(
            Theme.date_limite.is_not(None) & 
            (Theme.date_limite <= current_time)
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_theme(db: AsyncSession, theme_id: int, theme_data: ThemeUpdate) -> Optional[Theme]:
        """Update a theme"""
        theme = await ThemeService.get_theme(db, theme_id)
        if not theme:
            return None

        update_data = theme_data.model_dump(exclude_unset=True)
        
        # Handle date_limite timezone conversion if present
        if 'date_limite' in update_data and update_data['date_limite'] is not None:
            date_limite = update_data['date_limite']
            if hasattr(date_limite, 'tzinfo') and date_limite.tzinfo is not None:
                update_data['date_limite'] = date_limite.astimezone(timezone.utc).replace(tzinfo=None)
        
        for field, value in update_data.items():
            setattr(theme, field, value)
        
        theme.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
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
