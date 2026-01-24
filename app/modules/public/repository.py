"""
Public module - Database repository for public API
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional, Tuple, List

from app.core.logging import get_logger
from app.models.manuscript import Manuscript
from app.models.user import User
from app.models.theme import Theme
from app.models.section import Section
from app.models.language import Language
from app.models.enums import ManuscriptStatus

logger = get_logger(__name__)


class PublicRepository:
    """Repository for public manuscript queries"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def search_published_manuscripts(
        self,
        query: Optional[str] = None,
        theme_id: Optional[int] = None,
        section_id: Optional[int] = None,
        language_id: Optional[int] = None,
        author_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Manuscript], int]:
        """
        Search published manuscripts with filters and pagination
        """
        logger.info(f"Searching published manuscripts: query={query}, theme={theme_id}, section={section_id}")
        
        # Base query - only published manuscripts
        base_query = select(Manuscript).where(
            Manuscript.status == ManuscriptStatus.PUBLISHED
        ).options(
            selectinload(Manuscript.author),
            selectinload(Manuscript.theme),
            selectinload(Manuscript.section),
            selectinload(Manuscript.language)
        )
        
        # Apply search filter
        if query:
            search_pattern = f"%{query}%"
            base_query = base_query.where(
                or_(
                    Manuscript.title.ilike(search_pattern),
                    Manuscript.abstract.ilike(search_pattern),
                    Manuscript.keywords.ilike(search_pattern)
                )
            )
        
        # Apply theme filter
        if theme_id:
            base_query = base_query.where(Manuscript.theme_id == theme_id)
        
        # Apply section filter
        if section_id:
            base_query = base_query.where(Manuscript.section_id == section_id)
        
        # Apply language filter
        if language_id:
            base_query = base_query.where(Manuscript.language_id == language_id)
        
        # Apply author filter
        if author_id:
            base_query = base_query.where(Manuscript.author_id == author_id)
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination and ordering
        offset = (page - 1) * page_size
        paginated_query = base_query.order_by(
            Manuscript.published_at.desc().nullslast(),
            Manuscript.created_at.desc()
        ).offset(offset).limit(page_size)
        
        result = await self.db.execute(paginated_query)
        manuscripts = result.scalars().all()
        
        logger.info(f"Found {len(manuscripts)} manuscripts (total: {total})")
        return list(manuscripts), total
    
    async def get_published_manuscript_by_id(self, manuscript_id: int) -> Optional[Manuscript]:
        """
        Get a single published manuscript by ID
        """
        logger.info(f"Fetching published manuscript id={manuscript_id}")
        
        query = select(Manuscript).where(
            Manuscript.id == manuscript_id,
            Manuscript.status == ManuscriptStatus.PUBLISHED
        ).options(
            selectinload(Manuscript.author),
            selectinload(Manuscript.theme),
            selectinload(Manuscript.section),
            selectinload(Manuscript.language)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_author_public_profile(self, author_id: int) -> Optional[User]:
        """
        Get author public profile
        """
        logger.info(f"Fetching public profile for author_id={author_id}")
        
        query = select(User).where(User.id == author_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_author_publications(self, author_id: int) -> Tuple[List[Manuscript], int]:
        """
        Get all published manuscripts by an author
        """
        logger.info(f"Fetching publications for author_id={author_id}")
        
        query = select(Manuscript).where(
            Manuscript.author_id == author_id,
            Manuscript.status == ManuscriptStatus.PUBLISHED
        ).options(
            selectinload(Manuscript.author),
            selectinload(Manuscript.theme),
            selectinload(Manuscript.section),
            selectinload(Manuscript.language)
        ).order_by(Manuscript.published_at.desc().nullslast())
        
        result = await self.db.execute(query)
        manuscripts = list(result.scalars().all())
        
        return manuscripts, len(manuscripts)
    
    async def get_all_themes(self) -> List[Theme]:
        """Get all themes for filters"""
        query = select(Theme).order_by(Theme.title)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all_sections(self) -> List[Section]:
        """Get all sections for filters"""
        query = select(Section).order_by(Section.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all_languages(self) -> List[Language]:
        """Get all languages for filters"""
        query = select(Language).order_by(Language.name)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_recent_publications(self, limit: int = 10) -> List[Manuscript]:
        """Get most recent published manuscripts"""
        query = select(Manuscript).where(
            Manuscript.status == ManuscriptStatus.PUBLISHED
        ).options(
            selectinload(Manuscript.author),
            selectinload(Manuscript.theme),
            selectinload(Manuscript.section),
            selectinload(Manuscript.language)
        ).order_by(
            Manuscript.published_at.desc().nullslast(),
            Manuscript.created_at.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_stats(self) -> dict:
        """Get public statistics"""
        # Count published manuscripts
        pub_count = await self.db.execute(
            select(func.count(Manuscript.id)).where(
                Manuscript.status == ManuscriptStatus.PUBLISHED
            )
        )
        published_count = pub_count.scalar() or 0
        
        # Count unique authors with publications
        author_count = await self.db.execute(
            select(func.count(func.distinct(Manuscript.author_id))).where(
                Manuscript.status == ManuscriptStatus.PUBLISHED
            )
        )
        authors_count = author_count.scalar() or 0
        
        # Count themes with publications
        theme_count = await self.db.execute(
            select(func.count(func.distinct(Manuscript.theme_id))).where(
                Manuscript.status == ManuscriptStatus.PUBLISHED,
                Manuscript.theme_id.isnot(None)
            )
        )
        themes_count = theme_count.scalar() or 0
        
        return {
            "publishedManuscripts": published_count,
            "authors": authors_count,
            "themes": themes_count
        }
