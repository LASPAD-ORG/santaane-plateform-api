"""
API routes for evaluator assignment management
"""
from fastapi import APIRouter, Depends, status
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import require_any_role, get_current_user
from app.core.roles import UserRole
from app.models.user import User
from app.modules.manuscripts.evaluator_schemas import (
    EvaluatorAssignRequest,
    EvaluatorResponseRequest
)
from app.modules.manuscripts.evaluator_service import EvaluatorAssignmentService


router = APIRouter(prefix="/manuscripts", tags=["Manuscript Evaluators"])


@router.post(
    "/{manuscript_id}/assign-evaluator",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_any_role(UserRole.EDITOR, UserRole.SUPER_ADMIN))],
    summary="Assign evaluator to manuscript"
)
async def assign_evaluator_to_manuscript(
    manuscript_id: int,
    data: EvaluatorAssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign an evaluator to a manuscript for review.
    
    **Requires:** EDITOR or SUPER_ADMIN role
    
    **Parameters:**
    - **manuscript_id**: ID of the manuscript
    - **evaluatorId**: ID of the evaluator to assign
    - **evaluationDeadline**: Deadline for the evaluation
    
    **Process:**
    1. Validates manuscript and evaluator exist
    2. Creates assignment with PENDING status
    3. Sends evaluation request email to evaluator
    4. Email includes manuscript PDF link and deadline
    
    **Returns:** Assignment details with status
    """
    service = EvaluatorAssignmentService(db)
    return await service.assign_evaluator(
        manuscript_id=manuscript_id,
        evaluator_id=data.evaluator_id,
        evaluation_deadline=data.evaluation_deadline,
        assigned_by_id=current_user.id
    )


@router.put(
    "/{manuscript_id}/evaluator-response",
    dependencies=[Depends(require_any_role(UserRole.EVALUATOR, UserRole.SUPER_ADMIN))],
    summary="Accept or decline evaluation assignment"
)
async def respond_to_evaluation_assignment(
    manuscript_id: int,
    data: EvaluatorResponseRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluator accepts or declines an evaluation assignment.
    
    **Requires:** EVALUATOR role
    
    **Parameters:**
    - **manuscript_id**: ID of the manuscript
    - **accept**: true to accept, false to decline
    
    **Process:**
    - If **accept = true**: Updates status to ACCEPTED, sets response_at timestamp
    - If **accept = false**: Deletes the assignment (declined assignments are removed)
    
    **Returns:** Response status
    """
    service = EvaluatorAssignmentService(db)
    return await service.respond_to_assignment(
        manuscript_id=manuscript_id,
        evaluator_id=current_user.id,
        accept=data.accept
    )
