"""
API routes for manuscript evaluation grids
Endpoints for evaluators to create, update, and submit evaluation grids
"""
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_db
from app.core.permissions import require_role, get_current_user
from app.core.roles import UserRole
from app.models.user import User
from app.modules.manuscripts.evaluation_grid_service import EvaluationGridService
from app.modules.manuscripts.evaluation_grid_schemas import (
    SaveEvaluationGridRequest,
    EvaluationGridResponse,
    SubmitEvaluationResponse,
    ManuscriptEvaluationStatusResponse
)


router = APIRouter(prefix="/manuscripts", tags=["Evaluation Grids"])


@router.get(
    "/{manuscript_id}/evaluation-grid",
    response_model=EvaluationGridResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.EVALUATOR))],
    summary="Get evaluation grid",
    description="Retrieve the evaluation grid for a manuscript by the current evaluator"
)
async def get_evaluation_grid_endpoint(
    manuscript_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the evaluation grid for a manuscript.

    - **manuscript_id**: ID of the manuscript
    - Returns the evaluation grid with article title and evaluator name
    - Returns 404 if grid not found
    - Returns 403 if evaluator not assigned to manuscript
    """
    service = EvaluationGridService(db)
    return await service.get_evaluation_grid(
        manuscript_id=manuscript_id,
        evaluator_id=current_user.id
    )


@router.put(
    "/{manuscript_id}/evaluation-grid",
    response_model=EvaluationGridResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.EVALUATOR))],
    summary="Save evaluation grid (UPSERT)",
    description="Create or update the evaluation grid for a manuscript (draft mode)"
)
async def save_evaluation_grid_endpoint(
    manuscript_id: int,
    data: SaveEvaluationGridRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or update evaluation grid (UPSERT).

    - **manuscript_id**: ID of the manuscript
    - **data**: Evaluation grid data (all required fields)
    - Creates new grid if doesn't exist
    - Updates existing grid if exists and not submitted
    - Returns 403 if grid already submitted
    - Returns 403 if evaluator not assigned to manuscript
    """
    service = EvaluationGridService(db)
    return await service.save_evaluation_grid(
        manuscript_id=manuscript_id,
        evaluator_id=current_user.id,
        data=data
    )


@router.post(
    "/{manuscript_id}/submit-evaluation",
    response_model=SubmitEvaluationResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.EVALUATOR))],
    summary="Submit evaluation",
    description="Submit the final evaluation (locks the grid from further modifications)"
)
async def submit_evaluation_endpoint(
    manuscript_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit the evaluation grid and lock it from further modifications.

    - **manuscript_id**: ID of the manuscript
    - Sets submitted_at timestamp
    - Validates all required fields are filled
    - Returns summary with annotations count
    - Returns 404 if grid not found
    - Returns 400 if required fields incomplete
    - Returns 403 if evaluator not assigned to manuscript
    """
    service = EvaluationGridService(db)
    return await service.submit_evaluation(
        manuscript_id=manuscript_id,
        evaluator_id=current_user.id
    )


@router.get(
    "/{manuscript_id}/evaluation-status",
    response_model=ManuscriptEvaluationStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get manuscript evaluation status",
    description="Get evaluation progress and status for a manuscript"
)
async def get_manuscript_evaluation_status(
    manuscript_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the evaluation status for a manuscript.

    - **manuscript_id**: ID of the manuscript
    - Returns evaluation status, counts, and progress
    - Available to editors and evaluators
    """
    service = EvaluationGridService(db)
    return await service.get_manuscript_evaluation_status(
        manuscript_id=manuscript_id
    )
