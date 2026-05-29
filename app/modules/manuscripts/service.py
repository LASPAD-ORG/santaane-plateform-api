"""
Manuscripts module - Business logic service
Handles manuscript business logic
"""
from fastapi import HTTPException, status
from typing import List
from datetime import datetime, timedelta
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
    EvaluatorManuscriptResponse,
    CoauthorResponse
)
from app.models.coauthor import Coauthor
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

        # Create co-authors if provided
        coauthor_responses = []
        if manuscript_data.coauthors:
            coauthors_to_create = []
            for idx, coauthor_data in enumerate(manuscript_data.coauthors, start=1):
                coauthor = Coauthor(
                    manuscript_id=created_manuscript.id,
                    order=idx,
                    first_name=coauthor_data.firstName,
                    last_name=coauthor_data.lastName,
                    email=coauthor_data.email,
                    institution=coauthor_data.institution,
                    orcid_id=coauthor_data.orcidId
                )
                coauthors_to_create.append(coauthor)

            created_coauthors = await self.repository.create_coauthors(coauthors_to_create)
            coauthor_responses = [
                CoauthorResponse(
                    id=c.id,
                    firstName=c.first_name,
                    lastName=c.last_name,
                    email=c.email,
                    institution=c.institution,
                    orcidId=c.orcid_id,
                    order=c.order
                ) for c in created_coauthors
            ]
            logger.info(f"Created {len(created_coauthors)} co-authors for manuscript {created_manuscript.id}")

        # Fetch related data for response
        theme = await self.repository.get_theme_by_id(created_manuscript.theme_id) if created_manuscript.theme_id else None
        
        # Récupérer les informations de l'auteur pour l'email
        author = await self.repository.get_user_by_id(author_id)
        
        # Récupérer la langue du manuscrit
        language = await self.repository.get_language_by_id(manuscript_data.languageId)
        manuscript_lang = language.code if language else 'fr'
        
        # Envoyer notification au système
        try:
            from app.models.user import User
            from app.models.user_role import UserRole
            from sqlalchemy import select as sa_select

            # Récupérer tous les éditeurs actifs (role_id = 2)
            editors_result = await self.repository.session.execute(
                sa_select(User)
                .join(UserRole, UserRole.user_id == User.id)
                .where(UserRole.role_id == 2)
                .where(User.is_active == True)
            )
            editors = editors_result.scalars().all()
            editor_emails = [e.email for e in editors if e.email]

            # Notifier l'adresse système
            EmailService.send_system_new_submission_notification(
                manuscript_id=created_manuscript.id,
                manuscript_title=created_manuscript.title,
                author_name=author.full_name if author else "Auteur inconnu",
                author_email=author.email if author else "",
                section_name=section.name,
                theme_name=theme.title if theme else None,
                lang=manuscript_lang
            )

            # Notifier chaque éditeur
            for editor_email in editor_emails:
                EmailService.send_email(
                    to_email=editor_email,
                    subject=f"Nouvelle soumission - {created_manuscript.title[:50]}...",
                    body=EmailService._get_base_template(
                        "Nouvelle soumission de manuscrit",
                        f"""<div style="color: #333;">
                        <p style="font-size: 15px;">Un nouvel article a été soumis et nécessite votre attention.</p>
                        <table style="width:100%;border-collapse:collapse;margin:25px 0;">
                            <tr><td style="padding:12px;background:#f5f5f5;border:1px solid #ddd;font-weight:bold;width:30%;">Titre</td>
                                <td style="padding:12px;border:1px solid #ddd;"><strong>{created_manuscript.title}</strong></td></tr>
                            <tr><td style="padding:12px;background:#f5f5f5;border:1px solid #ddd;font-weight:bold;">Auteur</td>
                                <td style="padding:12px;border:1px solid #ddd;">{author.full_name if author else "Inconnu"} ({author.email if author else ""})</td></tr>
                            <tr><td style="padding:12px;background:#f5f5f5;border:1px solid #ddd;font-weight:bold;">Section</td>
                                <td style="padding:12px;border:1px solid #ddd;">{section.name}</td></tr>
                            <tr><td style="padding:12px;background:#f5f5f5;border:1px solid #ddd;font-weight:bold;">ID</td>
                                <td style="padding:12px;border:1px solid #ddd;">#{created_manuscript.id}</td></tr>
                        </table>
                        <div style="text-align:center;margin:35px 0;">
                            <a href="https://www.globalafricajournal.org/dashboard/editor/manuscripts/{created_manuscript.id}"
                               style="display:inline-block;padding:15px 40px;background:linear-gradient(135deg,#59a498 0%,#4a8a7f 100%);color:#ffffff;text-decoration:none;border-radius:8px;font-size:16px;font-weight:600;">
                                Voir le manuscrit
                            </a>
                        </div></div>"""
                    )
                )
            logger.info(f"Notifications envoyées à {len(editor_emails)} éditeur(s)")
        except Exception as e:
            logger.error(f"Erreur notification éditeurs: {str(e)}")
	
        
        # Envoyer confirmation à l'auteur
        try:
            if author and author.email:
                EmailService.send_author_submission_confirmation_email(
                    to_email=author.email,
                    author_name=author.full_name,
                    manuscript_title=created_manuscript.title,
                    submission_date=datetime.utcnow().strftime("%d/%m/%Y"),
                    manuscript_id=str(created_manuscript.id),
                    lang=manuscript_lang  # Utilisation de la langue du manuscrit
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
            coauthors=coauthor_responses,
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

            # Load co-authors for this manuscript
            coauthors = await self.repository.get_coauthors_by_manuscript(manuscript.id)
            coauthor_responses = [
                CoauthorResponse(
                    id=c.id,
                    firstName=c.first_name,
                    lastName=c.last_name,
                    email=c.email,
                    institution=c.institution,
                    orcidId=c.orcid_id,
                    order=c.order
                ) for c in coauthors
            ]

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
                    coauthors=coauthor_responses,
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

            # Load co-authors for this manuscript
            coauthors = await self.repository.get_coauthors_by_manuscript(manuscript.id)
            coauthor_responses = [
                CoauthorResponse(
                    id=c.id,
                    firstName=c.first_name,
                    lastName=c.last_name,
                    email=c.email,
                    institution=c.institution,
                    orcidId=c.orcid_id,
                    order=c.order
                ) for c in coauthors
            ]

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
                    coauthors=coauthor_responses,
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

        # Load co-authors
        coauthors = await self.repository.get_coauthors_by_manuscript(manuscript.id)
        coauthor_responses = [
            CoauthorResponse(
                id=c.id,
                firstName=c.first_name,
                lastName=c.last_name,
                email=c.email,
                institution=c.institution,
                orcidId=c.orcid_id,
                order=c.order
            ) for c in coauthors
        ]

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
            coauthors=coauthor_responses,
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

        # Load co-authors
        coauthors = await self.repository.get_coauthors_by_manuscript(manuscript.id)
        coauthor_responses = [
            CoauthorResponse(
                id=c.id,
                firstName=c.first_name,
                lastName=c.last_name,
                email=c.email,
                institution=c.institution,
                orcidId=c.orcid_id,
                order=c.order
            ) for c in coauthors
        ]

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
            coauthors=coauthor_responses,
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

        # Update co-authors if provided
        coauthor_responses = []
        if revision_data.coauthors is not None:
            # Delete existing co-authors
            await self.repository.delete_coauthors_by_manuscript(manuscript_id)

            # Create new co-authors
            if revision_data.coauthors:
                coauthors_to_create = []
                for idx, coauthor_data in enumerate(revision_data.coauthors, start=1):
                    coauthor = Coauthor(
                        manuscript_id=manuscript_id,
                        order=idx,
                        first_name=coauthor_data.firstName,
                        last_name=coauthor_data.lastName,
                        email=coauthor_data.email,
                        institution=coauthor_data.institution,
                        orcid_id=coauthor_data.orcidId
                    )
                    coauthors_to_create.append(coauthor)

                created_coauthors = await self.repository.create_coauthors(coauthors_to_create)
                coauthor_responses = [
                    CoauthorResponse(
                        id=c.id,
                        firstName=c.first_name,
                        lastName=c.last_name,
                        email=c.email,
                        institution=c.institution,
                        orcidId=c.orcid_id,
                        order=c.order
                    ) for c in created_coauthors
                ]
                logger.info(f"Updated {len(created_coauthors)} co-authors for manuscript {manuscript_id}")
        else:
            # Load existing co-authors for response
            coauthors = await self.repository.get_coauthors_by_manuscript(manuscript_id)
            coauthor_responses = [
                CoauthorResponse(
                    id=c.id,
                    firstName=c.first_name,
                    lastName=c.last_name,
                    email=c.email,
                    institution=c.institution,
                    orcidId=c.orcid_id,
                    order=c.order
                ) for c in coauthors
            ]

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
            
            # Get manuscript language
            language = await self.repository.get_language_by_id(manuscript.language_id)
            manuscript_lang = language.code if language else 'fr'
            
            EmailService.send_manuscript_resubmitted_notification(
                manuscript_id=manuscript_id,
                manuscript_title=manuscript.title,
                author_name=author_name,
                author_email=author_email,
                revision_number=revision_number,
                lang=manuscript_lang
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
            coauthors=coauthor_responses,
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

        try:
            # Récupérer l'auteur avec plus d'informations de débogage
            author = await self.repository.get_user_by_id(updated_manuscript.author_id)
            
            if not author:
                logger.error(f"Auteur non trouvé pour le manuscrit {manuscript_id} (author_id={updated_manuscript.author_id})")
            else:
                logger.info(f"Auteur trouvé: ID={author.id}, Email={author.email}, Full Name={getattr(author, 'full_name', 'N/A')}")
                
                # Vérifier si l'auteur a un email valide
                if not hasattr(author, 'email') or not author.email:
                    logger.error(f"L'auteur {author.id} n'a pas d'email valide")
                else:
                    author_name = author.full_name if hasattr(author, 'full_name') and author.full_name else author.email.split('@')[0]
                    author_email = author.email
                    manuscript_lang = language.code if language else "fr"
                    
                    logger.info(f"Envoi des emails pour le manuscrit {manuscript_id} à {author_email} (langue: {manuscript_lang})")
                    
                    # Envoyer l'email de notification au système
                    try:
                        system_success = EmailService.send_system_submitted_docx_file(
                            manuscript_id=updated_manuscript.id,
                            manuscript_title=updated_manuscript.title,
                            author_name=author_name,
                            author_email=author_email,
                            lang=manuscript_lang
                        )
                        logger.info(f"Email système {'envoyé' if system_success else 'échoué'} pour le manuscrit {manuscript_id}")
                    except Exception as sys_email_error:
                        logger.error(f"Erreur lors de l'envoi de l'email système: {str(sys_email_error)}")
                        system_success = False
                    
                    # Envoyer l'email de confirmation à l'auteur
                    try:
                        author_success = EmailService.send_auteur_confirmation_docx_file(
                            to_email=author_email,
                            author_name=author_name,
                            manuscript_title=updated_manuscript.title,
                            manuscript_id=updated_manuscript.id,
                            lang=manuscript_lang
                        )
                        logger.info(f"Email auteur {'envoyé' if author_success else 'échoué'} pour le manuscrit {manuscript_id}")
                    except Exception as author_email_error:
                        logger.error(f"Erreur lors de l'envoi de l'email à l'auteur: {str(author_email_error)}")
                        author_success = False
                    
                    # Journaliser le résultat global
                    if system_success and author_success:
                        logger.info(f"Tous les emails ont été envoyés avec succès pour le manuscrit {manuscript_id}")
                    else:
                        logger.warning(
                            f"Échec partiel des emails pour le manuscrit {manuscript_id} "
                            f"(système={'succès' if system_success else 'échec'}, "
                            f"auteur={'succès' if author_success else 'échec'})"
                        )
        except Exception as e:
            logger.error(f"Échec critique lors de l'envoi des emails de soumission DOCX: {str(e)}", exc_info=True)

        # Load co-authors for response
        coauthors = await self.repository.get_coauthors_by_manuscript(manuscript_id)
        coauthor_responses = [
            CoauthorResponse(
                id=c.id,
                firstName=c.first_name,
                lastName=c.last_name,
                email=c.email,
                institution=c.institution,
                orcidId=c.orcid_id,
                order=c.order
            ) for c in coauthors
        ]

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
            coauthors=coauthor_responses,
            createdAt=updated_manuscript.created_at,
            updatedAt=updated_manuscript.updated_at
        )

    async def update_manuscript_by_staff(
        self,
        manuscript_id: int,
        update_data: ManuscriptUpdate,
        current_user_id: int  # Ajout de l'utilisateur courant
     ) -> ManuscriptDetailResponse:
        """
        Met à jour un manuscrit par un membre du staff et envoie des notifications
        
        Args:
            manuscript_id: ID du manuscrit à mettre à jour
            update_data: Données de mise à jour
            current_user_id: ID de l'utilisateur effectuant la mise à jour
            
        Returns:
            ManuscriptDetailResponse: Détails du manuscrit mis à jour
        """
        logger.info(f"Staff updating manuscript {manuscript_id}")

        # Récupérer le manuscrit original pour comparer les changements
        manuscript = await self.repository.get_manuscript_by_id(manuscript_id)
        
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )
            
        # Récupérer l'auteur pour l'envoi d'email
        author = await self.repository.get_user_by_id(manuscript.author_id)
        if not author:
            logger.error(f"Auteur non trouvé pour le manuscrit {manuscript_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Auteur du manuscrit introuvable"
            )
            
        # Récupérer l'éditeur qui effectue la modification
        editor = await self.repository.get_user_by_id(current_user_id)
        if not editor:
            logger.error(f"Éditeur non trouvé (ID: {current_user_id})")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur éditeur introuvable"
            )

        # Dictionnaire pour suivre les changements
        changes = {}
        
        # Fonction utilitaire pour ajouter un changement
        def track_change(field_name, old_value, new_value):
            if old_value != new_value:
                changes[field_name] = (str(old_value), str(new_value) if new_value is not None else "Non spécifié")

        # Validation et suivi des changements
        if update_data.themeId is not None:
            theme = await self.repository.get_theme_by_id(update_data.themeId)
            if not theme:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_THEME_ID
                )
            track_change("Thème", manuscript.theme_id, update_data.themeId)
            manuscript.theme_id = update_data.themeId

        if update_data.sectionId is not None:
            section = await self.repository.get_section_by_id(update_data.sectionId)
            if not section:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_SECTION_ID
                )
            track_change("Section", manuscript.section_id, update_data.sectionId)
            manuscript.section_id = update_data.sectionId

        if update_data.languageId is not None:
            language = await self.repository.get_language_by_id(update_data.languageId)
            if not language:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ManuscriptErrorCode.INVALID_LANGUAGE_ID
                )
            track_change("Langue", manuscript.language_id, update_data.languageId)
            manuscript.language_id = update_data.languageId

        # Mise à jour des autres champs avec suivi des changements
        if update_data.title is not None:
            track_change("Titre", manuscript.title, update_data.title)
            manuscript.title = update_data.title
            
        if update_data.abstract is not None:
            old_abstract = manuscript.abstract
            new_abstract = update_data.abstract
            if old_abstract != new_abstract:
                changes["Résumé"] = ("*** (contenu modifié)" if old_abstract else "Vide", 
                                   "*** (contenu modifié)" if new_abstract else "Vide")
            manuscript.abstract = new_abstract
            
        if update_data.keywords is not None:
            track_change("Mots-clés", manuscript.keywords, update_data.keywords)
            manuscript.keywords = update_data.keywords
            
        if update_data.pdfFilename is not None:
            track_change("Fichier PDF", manuscript.pdf_filename, update_data.pdfFilename)
            manuscript.pdf_filename = update_data.pdfFilename
            
        if update_data.docxFilename is not None:
            track_change("Fichier DOCX", manuscript.docx_filename, update_data.docxFilename)
            manuscript.docx_filename = update_data.docxFilename

        # Si des changements ont été effectués
        if changes:
            # Sauvegarder les modifications
            updated_manuscript = await self.repository.update_manuscript(manuscript)
            logger.info(f"Manuscript {manuscript_id} updated successfully by staff")
            
            # Récupérer la langue du manuscrit pour l'email
            manuscript_lang = (await self.repository.get_language_by_id(updated_manuscript.language_id)).code if updated_manuscript.language_id else "fr"
            
            # Envoyer les notifications
            try:
                # Notification à l'auteur
                if author.email:
                    author_success = await EmailService.send_manuscript_updated_author_notification(
                        to_email=author.email,
                        author_name=author.full_name,
                        manuscript_id=updated_manuscript.id,
                        manuscript_title=updated_manuscript.title,
                        changes=changes,
                        lang=manuscript_lang
                    )
                    logger.info(f"Notification de mise à jour envoyée à l'auteur: {'succès' if author_success else 'échec'}")
                
                # Notification au système
                system_success = await EmailService.send_manuscript_updated_system_notification(
                    manuscript_id=updated_manuscript.id,
                    manuscript_title=updated_manuscript.title,
                    author_name=author.full_name,
                    author_email=author.email,
                    editor_name=editor.full_name,
                    changes=changes,
                    lang=manuscript_lang
                )
                logger.info(f"Notification système de mise à jour: {'succès' if system_success else 'échec'}")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi des notifications: {str(e)}", exc_info=True)
        else:
            logger.info(f"Aucun changement détecté pour le manuscrit {manuscript_id}")
            updated_manuscript = manuscript

        # Return detailed response
        return await self.get_manuscript_detail_for_staff(manuscript_id)

    async def update_manuscript_status(
        self,
        manuscript_id: int,
        status_data: ManuscriptStatusUpdate
     ) -> ManuscriptDetailResponse:
        """
        Met à jour le statut d'un manuscrit et envoie une notification à l'auteur
        
        Args:
            manuscript_id: ID du manuscrit à mettre à jour
            status_data: Données de mise à jour du statut
            
        Returns:
            ManuscriptDetailResponse: Détails du manuscrit mis à jour
        """
        import asyncio
        from fastapi.concurrency import run_in_threadpool
        
        logger.info(f"Updating manuscript {manuscript_id} status to {status_data.status}")

        # Validation du statut
        if not status_data.validate_allowed_status():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le statut doit être REVISION_REQUESTED, ACCEPTED, REJECTED ou PUBLISHED"
            )

        # Récupération du manuscrit
        manuscript = await self.repository.get_manuscript_by_id(manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=ManuscriptErrorCode.MANUSCRIPT_NOT_FOUND
            )

        # Vérification de l'auteur
        author = manuscript.author
        if not author:
            logger.error(f"Auteur non trouvé pour le manuscrit {manuscript_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Auteur du manuscrit introuvable"
            )
            
        author_name = author.full_name or "Auteur"
        author_email = author.email
        if not author_email:
            logger.error(f"Email de l'auteur manquant pour le manuscrit {manuscript_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'auteur du manuscrit n'a pas d'email valide"
            )

        # Récupération de la langue du manuscrit
        manuscript_lang = await self._get_manuscript_language(manuscript_id)
        logger.info(f"Langue du manuscrit {manuscript_id}: {manuscript_lang}")

        # Mise à jour du statut
        manuscript.status = status_data.status
        now = datetime.utcnow()
        
        # Mise à jour des dates en fonction du statut
        if status_data.status in [ManuscriptStatus.ACCEPTED, ManuscriptStatus.REJECTED]:
            manuscript.decision_at = now
        
        if status_data.status == ManuscriptStatus.PUBLISHED:
            manuscript.published_at = now

        # Sauvegarde des modifications
        await self.repository.update_manuscript(manuscript)
        logger.info(f"Manuscript {manuscript_id} status changed to {status_data.status}")

        # Fonction pour envoyer l'email en arrière-plan
        async def send_email_async():
            try:
                if status_data.status == ManuscriptStatus.ACCEPTED:
                    await run_in_threadpool(
                        EmailService.send_manuscript_accepted_email,
                        to_email=author_email,
                        author_name=author_name,
                        manuscript_title=manuscript.title,
                        manuscript_id=manuscript.id,
                        custom_message=status_data.emailComment,
                        lang=manuscript_lang
                    )
                    logger.info(f"Email d'acceptation envoyé à {author_email}")
                    
                elif status_data.status == ManuscriptStatus.REJECTED:
                    logger.info(f"Full status_data: {status_data}")
                    logger.info(f"Email comment from status_data: {status_data.emailComment}")
                    await run_in_threadpool(
                        EmailService.send_manuscript_rejected_email,
                        to_email=author_email,
                        author_name=author_name,
                        manuscript_title=manuscript.title,
                        manuscript_id=manuscript.id,
                        rejection_reason=status_data.emailComment,
                        lang=manuscript_lang
                    )
                    logger.info(f"Email de rejet envoyé à {author_email}")
                    
                elif status_data.status == ManuscriptStatus.PUBLISHED:
                    publication_url = f"{EmailService.PLATFORM_URL}/publications/{manuscript.id}"
                    await run_in_threadpool(
                        EmailService.send_manuscript_published_email,
                        to_email=author_email,
                        author_name=author_name,
                        manuscript_title=manuscript.title,
                        manuscript_id=manuscript.id,
                        publication_url=publication_url,
                        custom_message=status_data.emailComment,
                        lang=manuscript_lang
                    )
                    logger.info(f"Email de publication envoyé à {author_email}")
                    
                elif status_data.status == ManuscriptStatus.REVISION_REQUESTED:
                    # Calcul de la date limite de révision (30 jours)
                    revision_deadline = now + timedelta(days=30)
                    revision_deadline_str = revision_deadline.strftime("%d/%m/%Y")
                    
                    await run_in_threadpool(
                        EmailService.send_revision_requested_email,
                        to_email=author_email,
                        author_name=author_name,
                        manuscript_title=manuscript.title,
                        manuscript_id=manuscript.id,
                        revision_comments=status_data.emailComment,
                        lang=manuscript_lang
                    )
                    logger.info(f"Demande de révision envoyée à {author_email}")
                    
            except Exception as e:
                logger.error(f"Échec de l'envoi de l'email de notification: {str(e)}", exc_info=True)
                # Ici, vous pourriez ajouter une notification à l'administrateur

        # Lancement de l'envoi d'email en arrière-plan
        try:
            asyncio.create_task(send_email_async())
        except Exception as e:
            logger.error(f"Échec de la planification de l'envoi d'email: {str(e)}", exc_info=True)

        # Retourne la réponse détaillée
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

def generate_editorial_filename(manuscript_title: str, editor_name: str, version: int) -> str:
    # Nettoyer le titre (enlever espaces et caractères spéciaux)
    clean_title = "".join(e for e in manuscript_title if e.isalnum())[:30]
    clean_editor = "".join(e for e in editor_name if e.isalnum())
    return f"version_{version}_{clean_title}_{clean_editor}.docx"