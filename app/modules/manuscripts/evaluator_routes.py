"""
API routes for evaluator assignment management
"""
from fastapi import APIRouter, Depends, status
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import require_any_role, get_current_user, require_role
from app.core.roles import UserRole
from app.models.user import User
from app.modules.manuscripts.evaluator_schemas import (
    EvaluatorAssignRequest,
    EvaluatorResponseRequest
)
from app.modules.manuscripts.evaluator_service import EvaluatorAssignmentService
from app.modules.manuscripts.evaluator_manuscript_service import EvaluatorManuscriptService


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


@router.get(
    "/{manuscript_id}/evaluation-status",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.EVALUATOR))],
    summary="Get manuscript evaluation status for current evaluator"
)
async def get_manuscript_evaluation_status_for_evaluator(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get evaluation status for a manuscript specific to the current evaluator.

    **Requires:** EVALUATOR role

    **Parameters:**
    - **manuscript_id**: ID of the manuscript

    **Returns:**
    - **evaluationStatus**: 'not_started', 'in_progress', or 'completed'

    **Status Logic:**
    - **not_started**: Evaluator assigned but no evaluation grid exists
    - **in_progress**: Evaluation grid exists but not submitted (submitted_at is NULL)
    - **completed**: Evaluation grid submitted (submitted_at is not NULL)

    **Errors:**
    - **403**: Evaluator not assigned to manuscript or hasn't accepted assignment
    """
    service = EvaluatorManuscriptService(db)
    evaluation_status = await service.get_manuscript_evaluation_status_for_evaluator(
        manuscript_id=manuscript_id,
        evaluator_id=current_user.id
    )

    return {
        "manuscriptId": manuscript_id,
        "evaluationStatus": evaluation_status
    }


@router.post(
    "/{manuscript_id}/evaluator/{evaluator_id}/send-reminder",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_any_role(UserRole.EDITOR, UserRole.SUPER_ADMIN))],
    summary="Send reminder email to evaluator"
)
async def send_reminder_to_evaluator(
    manuscript_id: int,
    evaluator_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a reminder email to an evaluator who hasn't responded to evaluation request.

    **Requires:** EDITOR or SUPER_ADMIN role

    **Parameters:**
    - **manuscript_id**: ID of the manuscript
    - **evaluator_id**: ID of the evaluator

    **Process:**
    1. Validates that assignment exists and is in PENDING status
    2. Sends reminder email to evaluator
    3. Email reminds evaluator to accept or decline the evaluation request

    **Returns:** Success message with evaluator email and manuscript title

    **Errors:**
    - **404**: Assignment not found
    - **400**: Assignment is not in PENDING status (already accepted/rejected)
    - **500**: Failed to send email
    """
    service = EvaluatorAssignmentService(db)
    return await service.send_reminder_email(
        manuscript_id=manuscript_id,
        evaluator_id=evaluator_id
    )
