"""
Service layer for manuscript evaluation grids
Handles business logic for evaluation grid CRUD operations
"""
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional

from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid
from app.models.manuscript import Manuscript
from app.models.user import User
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
from app.models.enums import EvaluatorAssignmentStatus
from app.models.manuscript_annotation import ManuscriptAnnotation
from app.modules.manuscripts.evaluation_grid_schemas import (
    SaveEvaluationGridRequest,
    EvaluationGridResponse,
    SubmitEvaluationResponse
)
from app.core.logging import get_logger

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
            existing_grid.originality_of_ideas = data.originalityOfIdeas
            existing_grid.methodology_rigor = data.methodologyRigor
            existing_grid.theoretical_approach = data.theoreticalApproach
            existing_grid.presentation_clarity = data.presentationClarity
            existing_grid.strengths = data.strengths
            existing_grid.weaknesses = data.weaknesses
            existing_grid.suggestions = data.suggestions if data.suggestions else None
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
                originality_of_ideas=data.originalityOfIdeas,
                methodology_rigor=data.methodologyRigor,
                theoretical_approach=data.theoreticalApproach,
                presentation_clarity=data.presentationClarity,
                strengths=data.strengths,
                weaknesses=data.weaknesses,
                suggestions=data.suggestions if data.suggestions else None,
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
            recommendation=grid_to_return.recommendation,
            createdAt=grid_to_return.created_at,
            updatedAt=grid_to_return.updated_at,
            submittedAt=grid_to_return.submitted_at
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

        # Validate all required fields are filled
        if not all([
            grid.originality_of_ideas,
            grid.methodology_rigor,
            grid.theoretical_approach,
            grid.presentation_clarity,
            grid.strengths,
            grid.weaknesses,
            grid.recommendation
        ]):
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
