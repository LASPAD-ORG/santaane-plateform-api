"""
Manuscripts module - Business logic service
Handles manuscript business logic
"""
from fastapi import HTTPException, status
from typing import List
from app.modules.manuscripts.repository import ManuscriptRepository
from app.modules.manuscripts.schemas import (
    ManuscriptSubmit, 
    ManuscriptResponse,
    ManuscriptListResponse,
    ManuscriptRevision,
    ManuscriptDetailResponse,
    AuthorInfo,
    ManuscriptUpdate,
    ManuscriptStatusUpdate,
    EvaluatorAssignment,
    EvaluatorManuscriptResponse
)
from app.modules.manuscripts.error_codes import ManuscriptErrorCode
from app.models.manuscript import Manuscript
from app.models.enums import ManuscriptStatus
from app.core.logging import get_logger
from app.core.email import EmailService
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)


class ManuscriptService:
    """Service for manuscript business logic"""

    def __init__(self, repository: ManuscriptRepository):
        """
        Initialise le service avec le repository
        Note: Le repository contient déjà une session qui sera utilisée
        """
        self.repository = repository
        
    async def _get_manuscript_language(self, manuscript_id: int) -> str:
        """
        Récupère le code de langue d'un manuscrit (par défaut 'fr' si non spécifié)
        
        Args:
            manuscript_id: ID du manuscrit
            
        Returns:
            str: Code de langue sur 2 caractères (ex: 'fr', 'en')
        """
        try:
            # Récupérer le manuscrit avec la relation language chargée
            manuscript = await self.repository.get_manuscript_by_id(manuscript_id)
            
            if not manuscript:
                logger.warning(f"Manuscrit {manuscript_id} non trouvé, utilisation de 'fr' par défaut")
                return 'fr'
                
            # Si la langue est chargée, retourner son code
            if hasattr(manuscript, 'language') and manuscript.language:
                return manuscript.language.code or 'fr'
                
            logger.warning(f"Aucune langue trouvée pour le manuscrit {manuscript_id}, utilisation de 'fr' par défaut")
            return 'fr'
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la langue du manuscrit {manuscript_id}: {str(e)}")
            return 'fr'

    async def _get_evaluator_evaluation_status(self, manuscript_id: int, evaluator_id: int) -> str:
        """
        Récupère le statut d'évaluation individuel d'un évaluateur pour un manuscrit
        Retourne: 'not_started', 'in_progress', ou 'completed'
        """
        from sqlmodel import select
        from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid
        
        # Vérifier s'il y a une grille d'évaluation pour cet évaluateur
        query = select(ManuscriptEvaluationGrid).where(
            ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
            ManuscriptEvaluationGrid.evaluator_id == evaluator_id
        )
        result = await self.repository.session.execute(query)
        evaluation_grid = result.scalar_one_or_none()
        
        if not evaluation_grid:
            return "not_started"
        elif evaluation_grid.submitted_at is None:
            return "in_progress"
        else:
            return "completed"

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
            docx_filename=manuscript_data.docxFilename,
            status=ManuscriptStatus.SUBMITTED
        )

        created_manuscript = await self.repository.create_manuscript(manuscript)
        logger.info(f"Manuscript {created_manuscript.id} submitted successfully by user {author_id}")

        # Fetch related data for response
        theme = await self.repository.get_theme_by_id(created_manuscript.theme_id) if created_manuscript.theme_id else None
        
        # Récupérer les informations de l'auteur pour l'email
        author = await self.repository.get_user_by_id(author_id)
        
        # Récupérer la langue du manuscrit
        language = await self.repository.get_language_by_id(manuscript_data.languageId)
        manuscript_lang = language.code if language else 'fr'
        
        # Envoyer notification au système
        EmailService.send_new_submission_notification(
            manuscript_id=created_manuscript.id,
            manuscript_title=created_manuscript.title,
            author_name=author.full_name if author else "Auteur inconnu",
            author_email=author.email if author else "",
            section_name=section.name,
            theme_name=theme.title if theme else None,
            lang=manuscript_lang
        )
        
        # Envoyer confirmation à l'auteur
        try:
            if author and author.email:
                EmailService.send_submission_confirmation_email(
                    to_email=author.email,
                    author_name=author.full_name,
                    manuscript_title=created_manuscript.title,
                    manuscript_id=created_manuscript.id,
                    lang=manuscript_lang
                )
                logger.info(f"Submission confirmation email sent to {author.email}")
        except Exception as e:
            logger.error(f"Failed to send submission confirmation email: {str(e)}")
        
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
            docxFilename=created_manuscript.docx_filename,
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
        from sqlmodel import select
        from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
        from app.models.user import User
        from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid
        from app.modules.manuscripts.schemas import EvaluatorAssignment

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

            # Load evaluator assignments for this manuscript
            evaluator_assignments = []
            stmt = (
                select(ManuscriptEvaluatorLink, User)
                .join(User, ManuscriptEvaluatorLink.evaluator_id == User.id)
                .where(ManuscriptEvaluatorLink.manuscript_id == manuscript.id)
            )
            result = await self.repository.session.execute(stmt)
            links = result.all()

            for link, evaluator in links:
                # Check if evaluation grid is submitted
                grid_stmt = select(ManuscriptEvaluationGrid).where(
                    ManuscriptEvaluationGrid.manuscript_id == manuscript.id,
                    ManuscriptEvaluationGrid.evaluator_id == link.evaluator_id
                )
                grid_result = await self.repository.session.execute(grid_stmt)
                grid = grid_result.scalar_one_or_none()

                evaluation_status = "completed" if (grid and grid.submitted_at) else "in_progress" if grid else "not_started"

                evaluator_assignments.append(
                    EvaluatorAssignment(
                        evaluatorId=link.evaluator_id,
                        evaluatorName=evaluator.full_name or evaluator.email,
                        evaluatorEmail=evaluator.email,
                        status=link.status,
                        assignedAt=link.assigned_at,
                        responseAt=link.response_at,
                        evaluationDeadline=link.evaluation_deadline,
                        evaluationStatus=evaluation_status
                    )
                )

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
                    docxFilename=manuscript.docx_filename,
                    evaluators=evaluator_assignments,
                    createdAt=manuscript.created_at,
                    updatedAt=manuscript.updated_at
                )
            )

        return ManuscriptListResponse(
            manuscripts=manuscript_responses,
            total=total
        )

    async def get_all_manuscripts(
        self,
        theme_id: int | None = None,
        section_id: int | None = None,
        language_id: int | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> ManuscriptListResponse:
        """Get all manuscripts with optional filters (for editors)"""
        logger.info(f"Fetching all manuscripts with filters: theme={theme_id}, section={section_id}, language={language_id}")

        manuscripts = await self.repository.get_all_manuscripts(
            theme_id=theme_id,
            section_id=section_id,
            language_id=language_id,
            skip=skip,
            limit=limit
        )
        total = await self.repository.count_all_manuscripts(
            theme_id=theme_id,
            section_id=section_id,
            language_id=language_id
        )

        manuscript_responses = []
        for manuscript in manuscripts:
            theme = await self.repository.get_theme_by_id(manuscript.theme_id) if manuscript.theme_id else None
            section = await self.repository.get_section_by_id(manuscript.section_id)
            language = await self.repository.get_language_by_id(manuscript.language_id)
            
            # Get evaluators assigned to this manuscript
            evaluators = await self.repository.get_manuscript_evaluators(manuscript.id)
            evaluator_assignments = []
            for link in evaluators:
                # Récupérer le statut d'évaluation individuel de l'évaluateur
                evaluation_status = await self._get_evaluator_evaluation_status(manuscript.id, link.evaluator_id)
                
                evaluator_assignments.append(
                    EvaluatorAssignment(
                        evaluatorId=link.evaluator_id,
                        evaluatorName=link.evaluator.full_name,
                        evaluatorEmail=link.evaluator.email,
                        status=link.status,
                        assignedAt=link.assigned_at,
                        responseAt=link.response_at,
                        evaluationDeadline=link.evaluation_deadline,
                        evaluationStatus=evaluation_status  # Nouveau champ
                    )
                )

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
                    docxFilename=manuscript.docx_filename,
                    evaluators=evaluator_assignments,
                    createdAt=manuscript.created_at,
                    updatedAt=manuscript.updated_at
                )
            )

        return ManuscriptListResponse(
            manuscripts=manuscript_responses,
            total=total
        )

    async def get_manuscript_detail_for_staff(
        self,
        manuscript_id: int
    ) -> ManuscriptDetailResponse:
        """Get detailed manuscript information for admin/editor/evaluator"""
        logger.info(f"Fetching manuscript details {manuscript_id} for staff")

        manuscript = await self.repository.get_manuscript_by_id(manuscript_id)
        
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        # Fetch author information
        author = await self.repository.get_user_by_id(manuscript.author_id)
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )

        # Fetch related data
        theme = await self.repository.get_theme_by_id(manuscript.theme_id) if manuscript.theme_id else None
        section = await self.repository.get_section_by_id(manuscript.section_id)
        language = await self.repository.get_language_by_id(manuscript.language_id)

        return ManuscriptDetailResponse(
            id=manuscript.id,
            title=manuscript.title,
            abstract=manuscript.abstract,
            keywords=manuscript.keywords,
            themeId=manuscript.theme_id,
            themeName=theme.title if theme else None,
            sectionId=manuscript.section_id,
            sectionName=section.name if section else "",
            languageId=manuscript.language_id,
            languageName=language.name if language else "",
            status=manuscript.status,
            pdfFilename=manuscript.pdf_filename,
            docxFilename=manuscript.docx_filename,
            author=AuthorInfo(
                email=author.email,
                fullName=author.full_name,
                orcidId=author.orcid_id,
                bio=author.bio,
                position=author.position,
                institution=author.institution
            ),
            createdAt=manuscript.created_at,
            updatedAt=manuscript.updated_at
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
            docxFilename=manuscript.docx_filename,
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
        if revision_data.docxFilename is not None:
            manuscript.docx_filename = revision_data.docxFilename
        
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

        # Send notification email to system about re-submission
        try:
            author = manuscript.author
            author_name = f"{author.full_name}" if author else "Auteur"
            author_email = author.email if author else ""
            
            # Calculate revision number (count of times manuscript was revised)
            revision_number = 1  # Default to 1 for first revision
            
            EmailService.send_manuscript_resubmitted_notification(
                manuscript_id=manuscript_id,
                manuscript_title=manuscript.title,
                author_name=author_name,
                author_email=author_email,
                revision_number=revision_number
            )
            logger.info(f"Re-submission notification sent for manuscript {manuscript_id}")
        except Exception as e:
            logger.error(f"Failed to send re-submission notification: {str(e)}")

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
            docxFilename=updated_manuscript.docx_filename,
            createdAt=updated_manuscript.created_at,
            updatedAt=updated_manuscript.updated_at
        )

    async def upload_docx_for_accepted_manuscript(
        self,
        manuscript_id: int,
        docx_filename: str,
        current_user_id: int
    ) -> ManuscriptResponse:
        """Upload DOCX file for an accepted manuscript (author only)"""
        logger.info(f"Author {current_user_id} uploading DOCX for manuscript {manuscript_id}")

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
                detail="You can only upload DOCX for your own manuscripts"
            )

        # Verify that the manuscript status is ACCEPTED
        if manuscript.status != ManuscriptStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"DOCX can only be uploaded for accepted manuscripts. Current status: '{manuscript.status.value}'"
            )

        # Validate docx_filename
        if not docx_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="DOCX filename is required"
            )

        # Update docx_filename
        manuscript.docx_filename = docx_filename

        # Save changes
        updated_manuscript = await self.repository.update_manuscript(manuscript)
        logger.info(f"DOCX uploaded successfully for manuscript {manuscript_id}")

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
            docxFilename=updated_manuscript.docx_filename,
            createdAt=updated_manuscript.created_at,
            updatedAt=updated_manuscript.updated_at
        )

    async def update_manuscript_by_staff(
        self,
        manuscript_id: int,
        update_data: ManuscriptUpdate
    ) -> ManuscriptDetailResponse:
        """Update manuscript by editor/admin (all fields except status)"""
        logger.info(f"Staff updating manuscript {manuscript_id}")

        manuscript = await self.repository.get_manuscript_by_id(manuscript_id)
        
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        # Validate theme if provided
        if update_data.themeId is not None:
            theme = await self.repository.get_theme_by_id(update_data.themeId)
            if not theme:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_THEME_ID
                )

        # Validate section if provided
        if update_data.sectionId is not None:
            section = await self.repository.get_section_by_id(update_data.sectionId)
            if not section:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_SECTION_ID
                )

        # Validate language if provided
        if update_data.languageId is not None:
            language = await self.repository.get_language_by_id(update_data.languageId)
            if not language:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_LANGUAGE_ID
                )

        # Update fields (all except status)
        if update_data.title is not None:
            manuscript.title = update_data.title
        if update_data.abstract is not None:
            manuscript.abstract = update_data.abstract
        if update_data.keywords is not None:
            manuscript.keywords = update_data.keywords
        if update_data.themeId is not None:
            manuscript.theme_id = update_data.themeId
        if update_data.sectionId is not None:
            manuscript.section_id = update_data.sectionId
        if update_data.languageId is not None:
            manuscript.language_id = update_data.languageId
        if update_data.pdfFilename is not None:
            manuscript.pdf_filename = update_data.pdfFilename
        if update_data.docxFilename is not None:
            manuscript.docx_filename = update_data.docxFilename

        updated_manuscript = await self.repository.update_manuscript(manuscript)
        logger.info(f"Manuscript {manuscript_id} updated successfully by staff")

        # Return detailed response
        return await self.get_manuscript_detail_for_staff(manuscript_id)

    async def update_manuscript_status(
        self,
        manuscript_id: int,
        status_data: ManuscriptStatusUpdate
    ) -> ManuscriptDetailResponse:
        """Update manuscript status (REVISION_REQUESTED, ACCEPTED, REJECTED, or PUBLISHED)"""
        from datetime import datetime
        
        logger.info(f"Updating manuscript {manuscript_id} status to {status_data.status}")

        # Validate allowed status
        if not status_data.validate_allowed_status():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status can only be REVISION_REQUESTED, ACCEPTED, REJECTED, or PUBLISHED"
            )

        manuscript = await self.repository.get_manuscript_by_id(manuscript_id)
        
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        # Update status
        manuscript.status = status_data.status
        
        # Update decision_at if status is ACCEPTED or REJECTED
        if status_data.status in [ManuscriptStatus.ACCEPTED, ManuscriptStatus.REJECTED]:
            manuscript.decision_at = datetime.utcnow()
        
        # Update published_at if status is PUBLISHED
        if status_data.status == ManuscriptStatus.PUBLISHED:
            manuscript.published_at = datetime.utcnow()

        await self.repository.update_manuscript(manuscript)
        logger.info(f"Manuscript {manuscript_id} status changed to {status_data.status}")

        # Send email notification to author based on status in a separate thread
        try:
            from fastapi.concurrency import run_in_threadpool
            
            author = manuscript.author
            author_name = f"{author.full_name}"
            author_email = author.email
            
            async def send_email_async():
                try:
                    if status_data.status == ManuscriptStatus.ACCEPTED:
                        # Récupérer la langue du manuscrit
                        manuscript_lang = await self._get_manuscript_language(manuscript_id)
                        
                        # Envoyer l'email d'acceptation dans la langue appropriée
                        await run_in_threadpool(
                            EmailService.send_manuscript_accepted_email,
                            to_email=author_email,
                            author_name=author_name,
                            manuscript_title=manuscript.title,
                            manuscript_id=manuscript_id,
                            lang=manuscript_lang
                        )
                        logger.info(f"Acceptance email sent to {author_email}")
                        
                    elif status_data.status == ManuscriptStatus.REJECTED:
                        await run_in_threadpool(
                            EmailService.send_manuscript_rejected_email,
                            to_email=author_email,
                            author_name=author_name,
                            manuscript_title=manuscript.title,
                            manuscript_id=manuscript_id,
                            rejection_reason=status_data.comment if hasattr(status_data, 'comment') else None
                        )
                        logger.info(f"Rejection email sent to {author_email}")
                        
                    elif status_data.status == ManuscriptStatus.PUBLISHED:
                        await run_in_threadpool(
                            EmailService.send_manuscript_published_email,
                            to_email=author_email,
                            author_name=author_name,
                            manuscript_title=manuscript.title,
                            manuscript_id=manuscript_id
                        )
                        logger.info(f"Publication email sent to {author_email}")
                        
                    elif status_data.status == ManuscriptStatus.REVISION_REQUESTED:
                        # Récupérer la langue du manuscrit
                        manuscript_lang = await self._get_manuscript_language(manuscript_id)
                        
                        # Envoyer l'email de demande de révision dans la langue appropriée
                        await run_in_threadpool(
                            EmailService.send_revision_requested_email,
                            to_email=author_email,
                            author_name=author_name,
                            manuscript_title=manuscript.title,
                            manuscript_id=manuscript_id,
                            revision_comments=status_data.comment if hasattr(status_data, 'comment') else None,
                            lang=manuscript_lang
                        )
                        logger.info(f"Revision request email sent to {author_email}")
                        
                except Exception as e:
                    logger.error(f"Failed to send status change email: {str(e)}")
            
            # Lancer l'envoi d'email en arrière-plan sans attendre la fin
            import asyncio
            asyncio.create_task(send_email_async())
            
        except Exception as e:
            logger.error(f"Failed to schedule status change email: {str(e)}")

        # Return detailed response
        return await self.get_manuscript_detail_for_staff(manuscript_id)

    async def get_my_assignments(self, evaluator_id: int) -> List[EvaluatorManuscriptResponse]:
        """Get all manuscripts assigned to an evaluator (without author details)"""
        logger.info(f"Fetching manuscript assignments for evaluator {evaluator_id}")
        
        assignments = await self.repository.get_manuscripts_for_evaluator(evaluator_id)
        
        manuscripts = []
        for assignment in assignments:
            manuscript = assignment.manuscript
            
            manuscripts.append(
                EvaluatorManuscriptResponse(
                    id=manuscript.id,
                    title=manuscript.title,
                    abstract=manuscript.abstract,
                    keywords=manuscript.keywords,
                    themeName=manuscript.theme.title if manuscript.theme else None,
                    sectionName=manuscript.section.name,
                    languageName=manuscript.language.name,
                    status=manuscript.status,
                    pdfFilename=manuscript.pdf_filename,
                    docxFilename=manuscript.docx_filename,
                    assignmentStatus=assignment.status,
                    assignedAt=assignment.assigned_at,
                    evaluationDeadline=assignment.evaluation_deadline,
                    responseAt=assignment.response_at,
                    createdAt=manuscript.created_at,
                    updatedAt=manuscript.updated_at
                )
            )
        
        logger.info(f"Found {len(manuscripts)} manuscript assignments for evaluator {evaluator_id}")
        return manuscripts
