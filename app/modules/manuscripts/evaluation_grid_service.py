"""
Service layer for manuscript evaluation grids
Handles business logic for evaluation grid CRUD operations
"""
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional

from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid
from app.models.manuscript import Manuscript
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
from app.models.enums import EvaluatorAssignmentStatus, ManuscriptEvaluationStatus
from app.models.manuscript_annotation import ManuscriptAnnotation
from app.modules.manuscripts.evaluation_grid_schemas import (
    SaveEvaluationGridRequest,
    EvaluationGridResponse,
    SubmitEvaluationResponse,
    ManuscriptEvaluationStatusResponse
)
from app.core.logging import get_logger
from app.core.email import EmailService

logger = get_logger(__name__)


class EvaluationGridService:
    """Service for managing manuscript evaluation grids"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _verify_evaluator_assignment(
        self,
        manuscript_id: int,
        evaluator_id: int
    ) -> None:
        """
        Verify that the evaluator is assigned to the manuscript and has accepted.
        Raises HTTPException if not assigned or not accepted.
        """
        query = select(ManuscriptEvaluatorLink).where(
            and_(
                ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
                ManuscriptEvaluatorLink.evaluator_id == evaluator_id
            )
        )
        result = await self.db.execute(query)
        assignment = result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'êtes pas assigné à ce manuscrit"
            )

        if assignment.status != EvaluatorAssignmentStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous devez accepter l'assignation avant de pouvoir évaluer"
            )

    async def _update_manuscript_evaluation_status(self, manuscript_id: int) -> None:
        """
        Update manuscript evaluation_status based on submitted evaluations.

        Logic:
        - PENDING: No evaluators assigned or accepted
        - IN_PROGRESS: At least 1 evaluator assigned and accepted, but none submitted
        - PARTIALLY_EVALUATED: Some evaluators submitted, but not all
        - FULLY_EVALUATED: All assigned evaluators have submitted
        """
        # Count assigned and accepted evaluators
        assigned_query = select(func.count(ManuscriptEvaluatorLink.manuscript_id)).where(
            ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
            ManuscriptEvaluatorLink.status == EvaluatorAssignmentStatus.ACCEPTED
        )
        assigned_result = await self.db.execute(assigned_query)
        assigned_count = assigned_result.scalar()

        # Count submitted evaluations
        submitted_query = select(func.count(ManuscriptEvaluationGrid.id)).where(
            ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
            ManuscriptEvaluationGrid.submitted_at.isnot(None)
        )
        submitted_result = await self.db.execute(submitted_query)
        submitted_count = submitted_result.scalar()

        # Get manuscript
        manuscript = await self.db.get(Manuscript, manuscript_id)
        if not manuscript:
            return

        # Determine new status
        if assigned_count == 0:
            new_status = ManuscriptEvaluationStatus.PENDING
        elif submitted_count == 0:
            new_status = ManuscriptEvaluationStatus.IN_PROGRESS
        elif submitted_count < assigned_count:
            new_status = ManuscriptEvaluationStatus.PARTIALLY_EVALUATED
        elif submitted_count == assigned_count:
            new_status = ManuscriptEvaluationStatus.FULLY_EVALUATED
        else:
            # Should not happen, but fallback
            new_status = ManuscriptEvaluationStatus.PARTIALLY_EVALUATED

        # Update if changed
        if manuscript.evaluation_status != new_status:
            logger.info(f"Updating manuscript {manuscript_id} evaluation status: {manuscript.evaluation_status} -> {new_status}")
            manuscript.evaluation_status = new_status
            self.db.add(manuscript)
            await self.db.commit()

    async def get_evaluation_grid(
        self,
        manuscript_id: int,
        evaluator_id: int
    ) -> EvaluationGridResponse:
        """
        Retrieve evaluation grid for a manuscript and evaluator.
        Returns 404 if not found.
        """
        logger.info(f"Getting evaluation grid for manuscript {manuscript_id} by evaluator {evaluator_id}")

        # Verify evaluator assignment
        await self._verify_evaluator_assignment(manuscript_id, evaluator_id)

        # Query with JOINs to get articleTitle and evaluatorName
        query = (
            select(ManuscriptEvaluationGrid, Manuscript.title, User.full_name)
            .join(Manuscript, ManuscriptEvaluationGrid.manuscript_id == Manuscript.id)
            .join(User, ManuscriptEvaluationGrid.evaluator_id == User.id)
            .where(
                and_(
                    ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
                    ManuscriptEvaluationGrid.evaluator_id == evaluator_id
                )
            )
        )

        result = await self.db.execute(query)
        row = result.first()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grille d'évaluation non trouvée"
            )

        grid, article_title, evaluator_name = row

        # Map to response schema
        return EvaluationGridResponse(
            id=grid.id,
            manuscriptId=grid.manuscript_id,
            evaluatorId=grid.evaluator_id,
            articleTitle=article_title,
            evaluatorName=evaluator_name,
            originalityOfIdeas=grid.originality_of_ideas,
            methodologyRigor=grid.methodology_rigor,
            theoreticalApproach=grid.theoretical_approach,
            presentationClarity=grid.presentation_clarity,
            strengths=grid.strengths,
            weaknesses=grid.weaknesses,
            suggestions=grid.suggestions or "",
            editorialLineFit=grid.editorial_line_fit,
            globalOpinion=grid.global_opinion,
            recommendation=grid.recommendation,
            createdAt=grid.created_at,
            updatedAt=grid.updated_at,
            submittedAt=grid.submitted_at
        )

    async def save_evaluation_grid(
        self,
        manuscript_id: int,
        evaluator_id: int,
        data: SaveEvaluationGridRequest
     ) -> EvaluationGridResponse:
        """
        Create or update evaluation grid (UPSERT).
        Returns 403 if already submitted.
        """
        logger.info(f"Saving evaluation grid for manuscript {manuscript_id} by evaluator {evaluator_id}")

        # Verify evaluator assignment
        await self._verify_evaluator_assignment(manuscript_id, evaluator_id)

        # Check if grid already exists
        query = select(ManuscriptEvaluationGrid).where(
            and_(
                ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
                ManuscriptEvaluationGrid.evaluator_id == evaluator_id
            )
        )
        result = await self.db.execute(query)
        existing_grid = result.scalar_one_or_none()

        if existing_grid:
            # Check if already submitted
            if existing_grid.submitted_at is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="La grille a déjà été soumise et ne peut plus être modifiée"
                )

            # UPDATE existing grid
            existing_grid.originality_of_ideas = data.originalityOfIdeas or ""
            existing_grid.methodology_rigor = data.methodologyRigor or ""
            existing_grid.theoretical_approach = data.theoreticalApproach or ""
            existing_grid.presentation_clarity = data.presentationClarity or ""
            existing_grid.strengths = data.strengths or ""
            existing_grid.weaknesses = data.weaknesses or ""
            existing_grid.suggestions = data.suggestions if data.suggestions else None
            existing_grid.editorial_line_fit = data.editorialLineFit
            existing_grid.global_opinion = data.globalOpinion
            existing_grid.recommendation = data.recommendation
            existing_grid.updated_at = datetime.utcnow()

            self.db.add(existing_grid)
            await self.db.commit()
            await self.db.refresh(existing_grid)

            grid_to_return = existing_grid
        else:
            # CREATE new grid
            new_grid = ManuscriptEvaluationGrid(
                manuscript_id=manuscript_id,
                evaluator_id=evaluator_id,
                originality_of_ideas=data.originalityOfIdeas or "",
                methodology_rigor=data.methodologyRigor or "",
                theoretical_approach=data.theoreticalApproach or "",
                presentation_clarity=data.presentationClarity or "",
                strengths=data.strengths or "",
                weaknesses=data.weaknesses or "",
                suggestions=data.suggestions if data.suggestions else None,
                editorial_line_fit=data.editorialLineFit,
                global_opinion=data.globalOpinion,
                recommendation=data.recommendation,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(new_grid)
            await self.db.commit()
            await self.db.refresh(new_grid)

            grid_to_return = new_grid

        # Get manuscript title and evaluator name for response
        manuscript = await self.db.get(Manuscript, manuscript_id)
        evaluator = await self.db.get(User, evaluator_id)

        return EvaluationGridResponse(
            id=grid_to_return.id,
            manuscriptId=grid_to_return.manuscript_id,
            evaluatorId=grid_to_return.evaluator_id,
            articleTitle=manuscript.title,
            evaluatorName=evaluator.full_name,
            originalityOfIdeas=grid_to_return.originality_of_ideas,
            methodologyRigor=grid_to_return.methodology_rigor,
            theoreticalApproach=grid_to_return.theoretical_approach,
            presentationClarity=grid_to_return.presentation_clarity,
            strengths=grid_to_return.strengths,
            weaknesses=grid_to_return.weaknesses,
            suggestions=grid_to_return.suggestions or "",
            editorialLineFit=grid_to_return.editorial_line_fit,
            globalOpinion=grid_to_return.global_opinion,
            recommendation=grid_to_return.recommendation,
            createdAt=grid_to_return.created_at,
            updatedAt=grid_to_return.updated_at,
            submittedAt=grid_to_return.submitted_at
        )

    async def editor_update_grid(
        self,
        manuscript_id: int,
        evaluator_id: int,
        data: SaveEvaluationGridRequest
    ) -> EvaluationGridResponse:
        """Permet a l'editeur de modifier une grille MEME deja soumise (sans toucher submitted_at)."""
        logger.info(f"Editor updating grid for manuscript {manuscript_id}, evaluator {evaluator_id}")

        query = select(ManuscriptEvaluationGrid).where(
            and_(
                ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
                ManuscriptEvaluationGrid.evaluator_id == evaluator_id
            )
        )
        result = await self.db.execute(query)
        grid = result.scalar_one_or_none()
        if grid is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grille d'evaluation introuvable pour cet evaluateur"
            )

        grid.originality_of_ideas = data.originalityOfIdeas or ""
        grid.methodology_rigor = data.methodologyRigor or ""
        grid.theoretical_approach = data.theoreticalApproach or ""
        grid.presentation_clarity = data.presentationClarity or ""
        grid.strengths = data.strengths or ""
        grid.weaknesses = data.weaknesses or ""
        grid.suggestions = data.suggestions if data.suggestions else None
        grid.editorial_line_fit = data.editorialLineFit
        grid.global_opinion = data.globalOpinion
        grid.recommendation = data.recommendation
        grid.updated_at = datetime.utcnow()
        # submitted_at INCHANGE : la grille reste soumise

        self.db.add(grid)
        await self.db.commit()
        await self.db.refresh(grid)

        manuscript = await self.db.get(Manuscript, manuscript_id)
        evaluator = await self.db.get(User, evaluator_id)
        return EvaluationGridResponse(
            id=grid.id,
            manuscriptId=grid.manuscript_id,
            evaluatorId=grid.evaluator_id,
            articleTitle=manuscript.title if manuscript else "",
            evaluatorName=evaluator.full_name if evaluator else "",
            originalityOfIdeas=grid.originality_of_ideas,
            methodologyRigor=grid.methodology_rigor,
            theoreticalApproach=grid.theoretical_approach,
            presentationClarity=grid.presentation_clarity,
            strengths=grid.strengths,
            weaknesses=grid.weaknesses,
            suggestions=grid.suggestions or "",
            editorialLineFit=grid.editorial_line_fit,
            globalOpinion=grid.global_opinion,
            recommendation=grid.recommendation,
            createdAt=grid.created_at,
            updatedAt=grid.updated_at,
            submittedAt=grid.submitted_at
        )

    async def submit_evaluation(
        self,
        manuscript_id: int,
        evaluator_id: int
     ) -> SubmitEvaluationResponse:
        """
        Submit the evaluation grid.
        Sets submitted_at timestamp and validates all required fields are filled.
        Returns 404 if grid not found, 400 if incomplete.
        """
        logger.info(f"Submitting evaluation for manuscript {manuscript_id} by evaluator {evaluator_id}")

        # Verify evaluator assignment
        await self._verify_evaluator_assignment(manuscript_id, evaluator_id)

        # Get existing grid
        query = select(ManuscriptEvaluationGrid).where(
            and_(
                ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
                ManuscriptEvaluationGrid.evaluator_id == evaluator_id
            )
        )
        result = await self.db.execute(query)
        grid = result.scalar_one_or_none()

        if not grid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grille d'évaluation non trouvée. Veuillez d'abord remplir la grille."
            )

        # Validate all required fields are filled (selon le type de grille)
        is_internal = (grid.recommendation or "").startswith("internal_")
        if is_internal:
            required_fields = [
                grid.editorial_line_fit,
                grid.originality_of_ideas,
                grid.theoretical_approach,
                grid.global_opinion,
                grid.recommendation,
            ]
        else:
            required_fields = [
                grid.originality_of_ideas,
                grid.methodology_rigor,
                grid.theoretical_approach,
                grid.presentation_clarity,
                grid.strengths,
                grid.weaknesses,
                grid.recommendation,
            ]
        if not all(required_fields):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La grille d'évaluation doit être complétée avant soumission"
            )

        # Mark as submitted
        grid.submitted_at = datetime.utcnow()
        grid.updated_at = datetime.utcnow()

        self.db.add(grid)
        await self.db.commit()
        await self.db.refresh(grid)

        # Update manuscript evaluation status
        await self._update_manuscript_evaluation_status(manuscript_id)

        # Get manuscript and evaluator details for email notification
        
        manuscript_query = select(Manuscript).where(Manuscript.id == manuscript_id)
        manuscript_result = await self.db.execute(manuscript_query)
        manuscript = manuscript_result.scalar_one_or_none()
        
        evaluator_query = select(User).where(User.id == evaluator_id)
        evaluator_result = await self.db.execute(evaluator_query)
        evaluator = evaluator_result.scalar_one_or_none()
        
        # Send notification to system
        try:
            logger.info(f"Sending evaluation submitted notification for manuscript {manuscript_id}")
            logger.info(f"Manuscript: {manuscript}")
            logger.info(f"Evaluator: {evaluator}")
            
            EmailService.send_evaluation_submitted_notification(
                manuscript_id=manuscript_id,
                manuscript_title=manuscript.title if manuscript else f"Manuscrit #{manuscript_id}",
                evaluator_name=evaluator.full_name if evaluator else "Évaluateur",
                evaluator_email=evaluator.email if evaluator else "",
                evaluation_decision=grid.recommendation or "Non spécifié"
            )
            logger.info(f"Evaluation submitted notification sent for manuscript {manuscript_id}")
            
            # Send notification to author
            logger.info(f"Preparing to send author notification for manuscript {manuscript_id}")
            logger.info(f"Manuscript object: {manuscript}")
            
            if manuscript and manuscript.author_id:
                try:
                    # Get author details separately
                    author_query = select(User).where(User.id == manuscript.author_id)
                    author_result = await self.db.execute(author_query)
                    author = author_result.scalar_one_or_none()
                    
                    logger.info(f"Manuscript author check: {author}")
                    logger.info(f"Manuscript ID: {manuscript.id}")
                    logger.info(f"Manuscript author_id: {manuscript.author_id}")
                    logger.info(f"Author object: {author}")
                    
                    if author:
                        manuscript_lang = manuscript.language or 'fr'  # Default to French if not set
                        logger.info(f"Author details: {author.full_name}, email: {author.email}, lang: {manuscript_lang}")
                        
                        # Send email to author using a simple synchronous call
                        try:
                            logger.info(f"Attempting to send evaluation submission email to author {author.email} for manuscript {manuscript_id}")
                            
                            # Use a simple synchronous call since EmailService methods are sync
                            result = EmailService.evaluator_send_evauation(
                                str(author.email),
                                str(author.full_name),
                                str(manuscript.title),
                                int(manuscript.id),
                                str(manuscript_lang)
                            )
                            
                            logger.info(f"EmailService.evaluator_send_evauation returned: {result}")
                            logger.info(f"Author notification sent for submitted evaluation of manuscript {manuscript_id}")
                        except Exception as e:
                            logger.error(f"Failed to send author notification email: {str(e)}", exc_info=True)
                    else:
                        logger.warning(f"Author not found for manuscript {manuscript_id}")
                except Exception as e:
                    logger.error(f"Failed to send author notification for submitted evaluation: {str(e)}")
            else:
                logger.warning(f"Cannot send author notification - manuscript or author is missing. Manuscript exists: {manuscript is not None}, Author ID exists: {manuscript.author_id if manuscript else 'N/A'}")
                    
        except Exception as e:
            logger.error(f"Failed to send evaluation submitted notification: {str(e)}")

        # Notifier tous les editeurs de la plateforme (evaluation interne ou externe)
        try:
            editors_query = (
                select(User)
                .join(UserRole, UserRole.user_id == User.id)
                .join(Role, Role.id == UserRole.role_id)
                .where(and_(Role.name == "EDITOR", User.is_active == True))
                .distinct()
            )
            editors_result = await self.db.execute(editors_query)
            editors = editors_result.scalars().all()
            logger.info(f"Notifying {len(editors)} editor(s) of submitted evaluation for manuscript {manuscript_id}")
            for editor in editors:
                try:
                    EmailService.send_evaluation_completed_to_editor(
                        to_email=str(editor.email),
                        editor_name=str(editor.full_name),
                        manuscript_title=manuscript.title if manuscript else f"Manuscrit #{manuscript_id}",
                        evaluator_name=evaluator.full_name if evaluator else "Evaluateur",
                        evaluation_decision=grid.recommendation or "Non specifie",
                        lang="fr",
                    )
                except Exception as e:
                    logger.error(f"Failed to notify editor {editor.email}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to fetch/notify editors: {str(e)}")

        # Count annotations
        annotations_query = select(ManuscriptAnnotation).where(
            and_(
                ManuscriptAnnotation.manuscript_id == manuscript_id,
                ManuscriptAnnotation.evaluator_id == evaluator_id
            )
        )
        annotations_result = await self.db.execute(annotations_query)
        annotations = annotations_result.scalars().all()

        # Build evaluation grid dict for response
        evaluation_grid_dict = {
            "id": grid.id,
            "originalityOfIdeas": grid.originality_of_ideas,
            "methodologyRigor": grid.methodology_rigor,
            "theoreticalApproach": grid.theoretical_approach,
            "presentationClarity": grid.presentation_clarity,
            "strengths": grid.strengths,
            "weaknesses": grid.weaknesses,
            "suggestions": grid.suggestions or "",
            "editorialLineFit": grid.editorial_line_fit,
            "globalOpinion": grid.global_opinion,
            "recommendation": grid.recommendation,
            "submittedAt": grid.submitted_at
        }

        return SubmitEvaluationResponse(
            message="Évaluation soumise avec succès",
            manuscriptId=manuscript_id,
            evaluatorId=evaluator_id,
            submittedAt=grid.submitted_at,
            annotationsCount=len(annotations),
            evaluationGrid=evaluation_grid_dict
        )

    async def get_manuscript_evaluation_status(
        self,
        manuscript_id: int
     ) -> ManuscriptEvaluationStatusResponse:
        """
        Get evaluation status for a manuscript.
        Returns counts and progress information.
        """
        logger.info(f"Getting evaluation status for manuscript {manuscript_id}")

        # Get manuscript
        manuscript = await self.db.get(Manuscript, manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscrit non trouvé"
            )

        # Count assigned and accepted evaluators
        assigned_query = select(func.count(ManuscriptEvaluatorLink.manuscript_id)).where(
            ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
            ManuscriptEvaluatorLink.status == EvaluatorAssignmentStatus.ACCEPTED
        )
        assigned_result = await self.db.execute(assigned_query)
        assigned_count = assigned_result.scalar()

        # Count submitted evaluations
        submitted_query = select(func.count(ManuscriptEvaluationGrid.id)).where(
            ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
            ManuscriptEvaluationGrid.submitted_at.isnot(None)
        )
        submitted_result = await self.db.execute(submitted_query)
        submitted_count = submitted_result.scalar()

        # Calculate progress
        progress = (submitted_count / assigned_count * 100) if assigned_count > 0 else 0
        is_fully_evaluated = assigned_count > 0 and submitted_count == assigned_count

        return ManuscriptEvaluationStatusResponse(
            manuscriptId=manuscript_id,
            evaluationStatus=manuscript.evaluation_status,
            assignedEvaluators=assigned_count,
            submittedEvaluations=submitted_count,
            isFullyEvaluated=is_fully_evaluated,
            progress=round(progress, 2)
        )

    async def validate_manuscript_evaluations(
        self,
        manuscript_id: int,
        editor_id: int,
        editor_message: Optional[str] = None,
    ) -> dict:
        """Valide globalement les evaluations d'un manuscrit (visibles par l'auteur) + email auteur."""
        manuscript = await self.db.get(Manuscript, manuscript_id)
        if manuscript is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscrit introuvable"
            )

        manuscript.evaluations_validated = True
        manuscript.evaluations_validated_at = datetime.utcnow()
        manuscript.evaluations_validated_by_id = editor_id
        manuscript.evaluations_editor_message = editor_message
        self.db.add(manuscript)
        await self.db.commit()
        await self.db.refresh(manuscript)

        logger.info(f"Evaluations validated for manuscript {manuscript_id} by editor {editor_id}")

        # Notifier l'auteur que ses evaluations sont disponibles
        try:
            author = await self.db.get(User, manuscript.author_id)
            if author and author.email:
                EmailService.send_evaluations_available_to_author(
                    to_email=str(author.email),
                    author_name=str(author.full_name),
                    manuscript_title=manuscript.title,
                    editor_message=editor_message,
                    lang="fr",
                )
                logger.info(f"Author {author.email} notified of available evaluations")
        except Exception as e:
            logger.error(f"Failed to notify author for manuscript {manuscript_id}: {str(e)}")

        return {
            "manuscriptId": manuscript_id,
            "validated": True,
            "validatedAt": manuscript.evaluations_validated_at,
            "message": "Evaluations validees et transmises a l'auteur"
        }
