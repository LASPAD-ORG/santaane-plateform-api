"""
Public module - Business logic service
"""
from typing import Optional
from math import ceil

from app.core.logging import get_logger
from app.modules.public.repository import PublicRepository
from app.modules.public.schemas import (
    PublicManuscriptSummary,
    PublicManuscriptDetail,
    PublicManuscriptListResponse,
    PublicAuthorInfo,
    PublicAuthorDetail
)

logger = get_logger(__name__)


class PublicService:
    """Service for public manuscript operations"""
    
    def __init__(self, repository: PublicRepository):
        self.repository = repository
    
    async def search_manuscripts(
        self,
        query: Optional[str] = None,
        theme_id: Optional[int] = None,
        section_id: Optional[int] = None,
        language_id: Optional[int] = None,
        author_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> PublicManuscriptListResponse:
        """
        Search published manuscripts with filters
        """
        logger.info(f"Public search: query={query}, page={page}")
        
        manuscripts, total = await self.repository.search_published_manuscripts(
            query=query,
            theme_id=theme_id,
            section_id=section_id,
            language_id=language_id,
            author_id=author_id,
            page=page,
            page_size=page_size
        )
        
        # Convert to response schema
        manuscript_summaries = []
        for m in manuscripts:
            manuscript_summaries.append(PublicManuscriptSummary(
                id=m.id,
                title=m.title,
                abstract=m.abstract,
                keywords=m.keywords,
                themeName=m.theme.title if m.theme else None,
                sectionName=m.section.name if m.section else "N/A",
                languageName=m.language.name if m.language else "N/A",
                authorName=m.author.full_name if m.author else "Anonyme",
                authorId=m.author_id,
                publishedAt=m.published_at,
                createdAt=m.created_at
            ))
        
        total_pages = ceil(total / page_size) if total > 0 else 1
        
        return PublicManuscriptListResponse(
            manuscripts=manuscript_summaries,
            total=total,
            page=page,
            pageSize=page_size,
            totalPages=total_pages
        )
    
    async def get_manuscript_detail(self, manuscript_id: int) -> Optional[PublicManuscriptDetail]:
        """
        Get detailed view of a published manuscript
        """
        logger.info(f"Getting manuscript detail: id={manuscript_id}")
        
        manuscript = await self.repository.get_published_manuscript_by_id(manuscript_id)
        
        if not manuscript:
            return None
        
        author_info = PublicAuthorInfo(
            id=manuscript.author.id,
            fullName=manuscript.author.full_name,
            orcidId=manuscript.author.orcid_id,
            bio=manuscript.author.bio,
            position=manuscript.author.position,
            institution=manuscript.author.institution
        ) if manuscript.author else None
        
        return PublicManuscriptDetail(
            id=manuscript.id,
            title=manuscript.title,
            abstract=manuscript.abstract,
            keywords=manuscript.keywords,
            themeId=manuscript.theme_id,
            themeName=manuscript.theme.title if manuscript.theme else None,
            sectionId=manuscript.section_id,
            sectionName=manuscript.section.name if manuscript.section else "N/A",
            languageId=manuscript.language_id,
            languageName=manuscript.language.name if manuscript.language else "N/A",
            pdfFilename=manuscript.pdf_filename,
            author=author_info,
            publishedAt=manuscript.published_at,
            createdAt=manuscript.created_at
        )
    
    async def get_author_profile(self, author_id: int) -> Optional[PublicAuthorDetail]:
        """
        Get author public profile with publications
        """
        logger.info(f"Getting author profile: id={author_id}")
        
        author = await self.repository.get_author_public_profile(author_id)
        
        if not author:
            return None
        
        manuscripts, count = await self.repository.get_author_publications(author_id)
        
        manuscript_summaries = []
        for m in manuscripts:
            manuscript_summaries.append(PublicManuscriptSummary(
                id=m.id,
                title=m.title,
                abstract=m.abstract,
                keywords=m.keywords,
                themeName=m.theme.title if m.theme else None,
                sectionName=m.section.name if m.section else "N/A",
                languageName=m.language.name if m.language else "N/A",
                authorName=author.full_name,
                authorId=author_id,
                publishedAt=m.published_at,
                createdAt=m.created_at
            ))
        
        return PublicAuthorDetail(
            id=author.id,
            fullName=author.full_name,
            orcidId=author.orcid_id,
            bio=author.bio,
            position=author.position,
            institution=author.institution,
            publicationsCount=count,
            manuscripts=manuscript_summaries
        )
    
    async def get_recent_publications(self, limit: int = 10):
        """
        Get most recent publications for homepage
        """
        logger.info(f"Getting recent publications, limit={limit}")
        
        manuscripts = await self.repository.get_recent_publications(limit)
        
        return [
            PublicManuscriptSummary(
                id=m.id,
                title=m.title,
                abstract=m.abstract,
                keywords=m.keywords,
                themeName=m.theme.title if m.theme else None,
                sectionName=m.section.name if m.section else "N/A",
                languageName=m.language.name if m.language else "N/A",
                authorName=m.author.full_name if m.author else "Anonyme",
                authorId=m.author_id,
                publishedAt=m.published_at,
                createdAt=m.created_at
            )
            for m in manuscripts
        ]
    
    async def get_filters(self):
        """
        Get available filter options
        """
        themes = await self.repository.get_all_themes()
        sections = await self.repository.get_all_sections()
        languages = await self.repository.get_all_languages()
        
        return {
            "themes": [{"id": t.id, "name": t.title} for t in themes],
            "sections": [{"id": s.id, "name": s.name} for s in sections],
            "languages": [{"id": l.id, "name": l.name} for l in languages]
        }
    
    async def get_stats(self):
        """
        Get public statistics for homepage
        """
        return await self.repository.get_stats()
