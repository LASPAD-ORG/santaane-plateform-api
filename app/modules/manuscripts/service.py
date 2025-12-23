"""
Manuscripts module - Business logic service
Handles manuscript business logic
"""
from fastapi import HTTPException, status
from app.modules.manuscripts.repository import ManuscriptRepository
from app.modules.manuscripts.schemas import (
    ManuscriptSubmit, 
    ManuscriptResponse,
    ManuscriptListResponse,
    ManuscriptRevision
)
from app.modules.manuscripts.error_codes import ManuscriptErrorCode
from app.models.manuscript import Manuscript
from app.models.enums import ManuscriptStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class ManuscriptService:
    """Service for manuscript business logic"""

    def __init__(self, repository: ManuscriptRepository):
        self.repository = repository

    async def submit_manuscript(
        self, 
        manuscript_data: ManuscriptSubmit, 
        author_id: int
    ) -> ManuscriptResponse:
        """Submit a new manuscript"""
        logger.info(f"Manuscript submission attempt by user {author_id}")

        # Validate theme if provided
        if manuscript_data.themeId is not None:
            theme = await self.repository.get_theme_by_id(manuscript_data.themeId)
            if not theme:
                logger.warning(f"Submission failed: invalid theme_id {manuscript_data.themeId}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_THEME_ID
                )

        # Validate section (required)
        section = await self.repository.get_section_by_id(manuscript_data.sectionId)
        if not section:
            logger.warning(f"Submission failed: invalid section_id {manuscript_data.sectionId}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ManuscriptErrorCode.INVALID_SECTION_ID
            )

        # Validate language (required)
        language = await self.repository.get_language_by_id(manuscript_data.languageId)
        if not language:
            logger.warning(f"Submission failed: invalid language_id {manuscript_data.languageId}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ManuscriptErrorCode.INVALID_LANGUAGE_ID
            )

        # Create manuscript
        manuscript = Manuscript(
            title=manuscript_data.title,
            abstract=manuscript_data.abstract,
            keywords=manuscript_data.keywords,
            author_id=author_id,
            theme_id=manuscript_data.themeId,
            section_id=manuscript_data.sectionId,
            language_id=manuscript_data.languageId,
            pdf_filename=manuscript_data.pdfFilename,
            status=ManuscriptStatus.SUBMITTED
        )

        created_manuscript = await self.repository.create_manuscript(manuscript)
        logger.info(f"Manuscript {created_manuscript.id} submitted successfully by user {author_id}")

        # Fetch related data for response
        theme = await self.repository.get_theme_by_id(created_manuscript.theme_id) if created_manuscript.theme_id else None
        
        return ManuscriptResponse(
            id=created_manuscript.id,
            title=created_manuscript.title,
            abstract=created_manuscript.abstract,
            keywords=created_manuscript.keywords,
            themeName=theme.title if theme else None,
            sectionName=section.name,
            languageName=language.name,
            status=created_manuscript.status,
            pdfFilename=created_manuscript.pdf_filename,
            createdAt=created_manuscript.created_at,
            updatedAt=created_manuscript.updated_at
        )

    async def get_my_manuscripts(
        self, 
        author_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> ManuscriptListResponse:
        """Get all manuscripts for the current author"""
        logger.info(f"Fetching manuscripts for user {author_id}")

        manuscripts = await self.repository.get_manuscripts_by_author(
            author_id=author_id,
            skip=skip,
            limit=limit
        )
        total = await self.repository.count_manuscripts_by_author(author_id)

        manuscript_responses = []
        for manuscript in manuscripts:
            theme = await self.repository.get_theme_by_id(manuscript.theme_id) if manuscript.theme_id else None
            section = await self.repository.get_section_by_id(manuscript.section_id)
            language = await self.repository.get_language_by_id(manuscript.language_id)

            manuscript_responses.append(
                ManuscriptResponse(
                    id=manuscript.id,
                    title=manuscript.title,
                    abstract=manuscript.abstract,
                    keywords=manuscript.keywords,
                    themeName=theme.title if theme else None,
                    sectionName=section.name if section else "",
                    languageName=language.name if language else "",
                    status=manuscript.status,
                    pdfFilename=manuscript.pdf_filename,
                    createdAt=manuscript.created_at,
                    updatedAt=manuscript.updated_at
                )
            )

        return ManuscriptListResponse(
            manuscripts=manuscript_responses,
            total=total
        )

    async def get_manuscript_details(
        self,
        manuscript_id: int,
        current_user_id: int
    ) -> ManuscriptResponse:
        """Get manuscript details by ID (only if user is the author)"""
        logger.info(f"Fetching manuscript {manuscript_id} for user {current_user_id}")

        manuscript = await self.repository.get_manuscript_by_id(manuscript_id)
        
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        # Verify that the current user is the author
        if manuscript.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your own manuscripts"
            )

        # Fetch related data
        theme = await self.repository.get_theme_by_id(manuscript.theme_id) if manuscript.theme_id else None
        section = await self.repository.get_section_by_id(manuscript.section_id)
        language = await self.repository.get_language_by_id(manuscript.language_id)

        return ManuscriptResponse(
            id=manuscript.id,
            title=manuscript.title,
            abstract=manuscript.abstract,
            keywords=manuscript.keywords,
            themeName=theme.title if theme else None,
            sectionName=section.name if section else "",
            languageName=language.name if language else "",
            status=manuscript.status,
            pdfFilename=manuscript.pdf_filename,
            createdAt=manuscript.created_at,
            updatedAt=manuscript.updated_at
        )

    async def revise_manuscript(
        self,
        manuscript_id: int,
        revision_data: "ManuscriptRevision",
        current_user_id: int
    ) -> "ManuscriptResponse":
        """Revise a manuscript (only if status is REVISION_REQUESTED)"""
        from app.models.enums import ManuscriptStatus
        from datetime import datetime
        
        logger.info(f"Manuscript {manuscript_id} revision attempt by user {current_user_id}")

        manuscript = await self.repository.get_manuscript_by_id(manuscript_id)
        
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        # Verify that the current user is the author
        if manuscript.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only revise your own manuscripts"
            )

        # Verify that the manuscript status is REVISION_REQUESTED
        if manuscript.status != ManuscriptStatus.REVISION_REQUESTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Manuscript can only be revised when status is 'revision_requested'. Current status: '{manuscript.status.value}'"
            )

        # Update fields if provided
        if revision_data.title is not None:
            manuscript.title = revision_data.title
        if revision_data.abstract is not None:
            manuscript.abstract = revision_data.abstract
        if revision_data.keywords is not None:
            manuscript.keywords = revision_data.keywords
        if revision_data.pdfFilename is not None:
            manuscript.pdf_filename = revision_data.pdfFilename
        
        # Validate and update theme if provided
        if revision_data.themeId is not None:
            theme = await self.repository.get_theme_by_id(revision_data.themeId)
            if not theme:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_THEME_ID
                )
            manuscript.theme_id = revision_data.themeId
        
        # Validate and update section if provided
        if revision_data.sectionId is not None:
            section = await self.repository.get_section_by_id(revision_data.sectionId)
            if not section:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_SECTION_ID
                )
            manuscript.section_id = revision_data.sectionId
        
        # Validate and update language if provided
        if revision_data.languageId is not None:
            language = await self.repository.get_language_by_id(revision_data.languageId)
            if not language:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_LANGUAGE_ID
                )
            manuscript.language_id = revision_data.languageId

        # Update status to RE_SUBMITTED
        manuscript.status = ManuscriptStatus.RE_SUBMITTED
        manuscript.last_revision_at = datetime.utcnow()

        # Save changes
        updated_manuscript = await self.repository.update_manuscript(manuscript)
        logger.info(f"Manuscript {manuscript_id} revised and re-submitted by user {current_user_id}")

        # Fetch related data for response
        theme = await self.repository.get_theme_by_id(updated_manuscript.theme_id) if updated_manuscript.theme_id else None
        section = await self.repository.get_section_by_id(updated_manuscript.section_id)
        language = await self.repository.get_language_by_id(updated_manuscript.language_id)

        return ManuscriptResponse(
            id=updated_manuscript.id,
            title=updated_manuscript.title,
            abstract=updated_manuscript.abstract,
            keywords=updated_manuscript.keywords,
            themeName=theme.title if theme else None,
            sectionName=section.name if section else "",
            languageName=language.name if language else "",
            status=updated_manuscript.status,
            pdfFilename=updated_manuscript.pdf_filename,
            createdAt=updated_manuscript.created_at,
            updatedAt=updated_manuscript.updated_at
        )
