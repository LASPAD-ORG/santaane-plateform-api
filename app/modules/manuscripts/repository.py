"""
Manuscripts module - Database repository
Handles database operations for manuscripts
"""
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from app.models.manuscript import Manuscript
from app.models.theme import Theme
from app.models.section import Section
from app.models.language import Language
from app.models.user import User
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink


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

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_manuscript(self, manuscript: Manuscript) -> Manuscript:
        """Create a new manuscript"""
        self.session.add(manuscript)
        await self.session.commit()
        await self.session.refresh(manuscript)
        return manuscript

    async def get_manuscript_by_id(self, manuscript_id: int) -> Optional[Manuscript]:
        """
        Get manuscript by ID with relationships loaded
        
        Args:
            manuscript_id: ID of the manuscript to retrieve
            
        Returns:
            Optional[Manuscript]: The manuscript with its relationships loaded, or None if not found
        """
        from sqlalchemy.orm import selectinload, joinedload
        
        result = await self.session.execute(
            select(Manuscript)
            .options(
                joinedload(Manuscript.language),
                selectinload(Manuscript.author)
            )
            .where(Manuscript.id == manuscript_id)
            .execution_options(populate_existing=True)
        )
        return result.unique().scalar_one_or_none()

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

    async def get_all_manuscripts(
        self,
        theme_id: int | None = None,
        section_id: int | None = None,
        language_id: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Manuscript]:
        """Get all manuscripts with optional filters"""
        query = select(Manuscript)
        
        # Apply filters
        if theme_id is not None:
            query = query.where(Manuscript.theme_id == theme_id)
        if section_id is not None:
            query = query.where(Manuscript.section_id == section_id)
        if language_id is not None:
            query = query.where(Manuscript.language_id == language_id)
        
        query = query.order_by(Manuscript.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_all_manuscripts(
        self,
        theme_id: int | None = None,
        section_id: int | None = None,
        language_id: int | None = None
    ) -> int:
        """Count all manuscripts with optional filters"""
        from sqlalchemy import func
        query = select(func.count(Manuscript.id))
        
        # Apply same filters
        if theme_id is not None:
            query = query.where(Manuscript.theme_id == theme_id)
        if section_id is not None:
            query = query.where(Manuscript.section_id == section_id)
        if language_id is not None:
            query = query.where(Manuscript.language_id == language_id)
        
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_manuscript_evaluators(self, manuscript_id: int) -> List[ManuscriptEvaluatorLink]:
        """Get all evaluators assigned to a manuscript with their information"""
        query = (
            select(ManuscriptEvaluatorLink)
            .where(ManuscriptEvaluatorLink.manuscript_id == manuscript_id)
            .options(selectinload(ManuscriptEvaluatorLink.evaluator))
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_manuscript(self, manuscript: Manuscript) -> Manuscript:
        """Update an existing manuscript"""
        self.session.add(manuscript)
        await self.session.commit()
        await self.session.refresh(manuscript)
        return manuscript

    async def get_manuscripts_for_evaluator(self, evaluator_id: int) -> List[ManuscriptEvaluatorLink]:
        """Get all manuscripts assigned to a specific evaluator"""
        query = (
            select(ManuscriptEvaluatorLink)
            .where(ManuscriptEvaluatorLink.evaluator_id == evaluator_id)
            .options(
                selectinload(ManuscriptEvaluatorLink.manuscript)
                .selectinload(Manuscript.theme)
            )
            .options(
                selectinload(ManuscriptEvaluatorLink.manuscript)
                .selectinload(Manuscript.section)
            )
            .options(
                selectinload(ManuscriptEvaluatorLink.manuscript)
                .selectinload(Manuscript.language)
            )
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
