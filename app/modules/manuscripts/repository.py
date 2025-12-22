"""
Manuscripts module - Database repository
Handles database operations for manuscripts
"""
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional
from app.models.manuscript import Manuscript
from app.models.theme import Theme
from app.models.section import Section
from app.models.language import Language


class ManuscriptRepository:
    """Repository for manuscript database operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_theme_by_id(self, theme_id: int) -> Optional[Theme]:
        """Get theme by ID"""
        result = await self.session.execute(
            select(Theme).where(Theme.id == theme_id)
        )
        return result.scalar_one_or_none()

    async def get_section_by_id(self, section_id: int) -> Optional[Section]:
        """Get section by ID"""
        result = await self.session.execute(
            select(Section).where(Section.id == section_id)
        )
        return result.scalar_one_or_none()

    async def get_language_by_id(self, language_id: int) -> Optional[Language]:
        """Get language by ID"""
        result = await self.session.execute(
            select(Language).where(Language.id == language_id)
        )
        return result.scalar_one_or_none()

    async def create_manuscript(self, manuscript: Manuscript) -> Manuscript:
        """Create a new manuscript"""
        self.session.add(manuscript)
        await self.session.commit()
        await self.session.refresh(manuscript)
        return manuscript

    async def get_manuscript_by_id(self, manuscript_id: int) -> Optional[Manuscript]:
        """Get manuscript by ID"""
        result = await self.session.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        return result.scalar_one_or_none()

    async def get_manuscripts_by_author(
        self, 
        author_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> list[Manuscript]:
        """Get all manuscripts by author"""
        result = await self.session.execute(
            select(Manuscript)
            .where(Manuscript.author_id == author_id)
            .order_by(Manuscript.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_manuscripts_by_author(self, author_id: int) -> int:
        """Count manuscripts by author"""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count(Manuscript.id)).where(Manuscript.author_id == author_id)
        )
        return result.scalar_one()
