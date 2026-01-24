"""
Service layer for manuscript evaluator assignment operations
Handles business logic for evaluator-specific manuscript queries
"""
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import and_
from fastapi import HTTPException, status
from typing import List

from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
from app.models.enums import EvaluatorAssignmentStatus
from app.core.logging import get_logger

logger = get_logger(__name__)


class EvaluatorManuscriptService:
    """Service for evaluator-specific manuscript operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_manuscript_evaluation_status_for_evaluator(
        self,
        manuscript_id: int,
        evaluator_id: int
    ) -> str:
        """
        Get evaluation status for a specific manuscript and evaluator.
        
        Returns:
        - 'not_started': Evaluator is assigned but hasn't started evaluation (no grid exists)
        - 'in_progress': Evaluator has started but not submitted (grid exists but submitted_at is NULL)
        - 'completed': Evaluator has submitted the evaluation (submitted_at is not NULL)
        
        Raises HTTPException if evaluator is not assigned to manuscript.
        """
        logger.info(f"Getting evaluation status for manuscript {manuscript_id} and evaluator {evaluator_id}")

        # Verify evaluator is assigned and has accepted
        assignment_query = select(ManuscriptEvaluatorLink).where(
            and_(
                ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
                ManuscriptEvaluatorLink.evaluator_id == evaluator_id,
                ManuscriptEvaluatorLink.status == EvaluatorAssignmentStatus.ACCEPTED
            )
        )
        assignment_result = await self.db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous n'êtes pas assigné à ce manuscrit ou vous n'avez pas accepté l'assignation"
            )

        # Check if evaluation grid exists
        grid_query = select(ManuscriptEvaluationGrid).where(
            and_(
                ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
                ManuscriptEvaluationGrid.evaluator_id == evaluator_id
            )
        )
        grid_result = await self.db.execute(grid_query)
        grid = grid_result.scalar_one_or_none()

        if not grid:
            # No grid exists, evaluation not started
            return 'not_started'
        
        if grid.submitted_at is None:
            # Grid exists but not submitted, evaluation in progress
            return 'in_progress'
        else:
            # Grid is submitted, evaluation completed
            return 'completed'