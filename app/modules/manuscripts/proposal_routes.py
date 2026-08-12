"""
API routes for external evaluator proposals.

- CREATE / DELETE : réservés à l'évaluateur interne du manuscrit.
- LIST : accessible à l'éditeur et à l'évaluateur interne.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db import get_db
from app.core.permissions import require_any_role, get_current_user
from app.core.roles import UserRole
from app.models.user import User
from app.modules.manuscripts.proposal_schemas import ProposalCreate, ProposalResponse, AssignProposalRequest, ProposalEnrichedResponse
from app.modules.manuscripts.proposal_service import ProposalService


router = APIRouter(prefix="/manuscripts", tags=["External Evaluator Proposals"])


@router.post(
    "/{manuscript_id}/proposed-evaluators",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_any_role(UserRole.INTERNAL_EVALUATOR, UserRole.SUPER_ADMIN))],
    summary="Internal evaluator proposes an external evaluator",
)
async def create_proposal(
    manuscript_id: int,
    data: ProposalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    L'évaluateur interne propose un évaluateur externe (nom, prénom, email).

    **Requires:** INTERNAL_EVALUATOR (doit être l'interne assigné à ce manuscrit)
    """
    service = ProposalService(db)
    return await service.create_proposal(manuscript_id, data, current_user.id)


@router.get(
    "/{manuscript_id}/proposed-evaluators",
    response_model=List[ProposalEnrichedResponse],
    dependencies=[Depends(require_any_role(
        UserRole.EDITOR, UserRole.SUPER_ADMIN, UserRole.INTERNAL_EVALUATOR
    ))],
    summary="List external evaluators proposed for a manuscript",
)
async def list_proposals(
    manuscript_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Liste les évaluateurs externes proposés pour un manuscrit.

    **Requires:** EDITOR, SUPER_ADMIN ou INTERNAL_EVALUATOR
    """
    service = ProposalService(db)
    return await service.list_proposals(manuscript_id)


@router.delete(
    "/{manuscript_id}/proposed-evaluators/{proposal_id}",
    dependencies=[Depends(require_any_role(UserRole.INTERNAL_EVALUATOR, UserRole.SUPER_ADMIN))],
    summary="Remove a proposed external evaluator",
)
async def delete_proposal(
    manuscript_id: int,
    proposal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Supprime une proposition.

    **Requires:** INTERNAL_EVALUATOR (doit être l'interne assigné à ce manuscrit)
    """
    service = ProposalService(db)
    return await service.delete_proposal(manuscript_id, proposal_id, current_user.id)


@router.post(
    "/{manuscript_id}/proposed-evaluators/{proposal_id}/assign",
    dependencies=[Depends(require_any_role(UserRole.EDITOR, UserRole.SUPER_ADMIN))],
    summary="Assign a proposed external evaluator (creates account if needed)",
)
async def assign_proposed_evaluator(
    manuscript_id: int,
    proposal_id: int,
    data: AssignProposalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Affecte un evaluateur externe propose au manuscrit.
    Cree le compte si necessaire (roles AUTHOR + EVALUATOR), ajoute le role
    EVALUATOR si le compte existe sans ce role, puis envoie l'invitation.
    **Requires:** EDITOR ou SUPER_ADMIN
    """
    service = ProposalService(db)
    return await service.assign_proposed_evaluator(
        manuscript_id, proposal_id, current_user.id, data.evaluation_deadline
    )
