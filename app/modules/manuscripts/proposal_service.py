"""
Service layer for external evaluator proposals.

Les propositions sont créées par l'évaluateur interne d'un manuscrit
(nom, prénom, email) et consultées par l'éditeur. Elles sont purement
informatives : l'éditeur reste libre de son choix final d'évaluateurs.
"""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models.external_evaluator_proposal import ExternalEvaluatorProposal
from app.models.manuscript import Manuscript
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
from app.models.enums import EvaluatorKind
from app.modules.manuscripts.proposal_schemas import ProposalCreate
from app.core.logging import logger


class ProposalService:
    """Service for managing external evaluator proposals."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _ensure_internal_evaluator(self, manuscript_id: int, user_id: int) -> None:
        """Vérifie que user_id est bien l'évaluateur interne (lien kind='internal') du manuscrit."""
        link_result = await self.db.execute(
            select(ManuscriptEvaluatorLink).where(
                ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
                ManuscriptEvaluatorLink.evaluator_id == user_id,
                ManuscriptEvaluatorLink.kind == EvaluatorKind.INTERNAL.value,
            )
        )
        if not link_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the internal evaluator of this manuscript"
            )

    async def create_proposal(
        self,
        manuscript_id: int,
        data: ProposalCreate,
        proposed_by_id: int,
    ) -> ExternalEvaluatorProposal:
        """L'évaluateur interne propose un évaluateur externe."""
        manuscript = await self.db.get(Manuscript, manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manuscript with ID {manuscript_id} not found"
            )

        await self._ensure_internal_evaluator(manuscript_id, proposed_by_id)

        # Éviter les doublons d'email pour un même manuscrit
        existing = await self.db.execute(
            select(ExternalEvaluatorProposal).where(
                ExternalEvaluatorProposal.manuscript_id == manuscript_id,
                ExternalEvaluatorProposal.email == data.email,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email has already been proposed for this manuscript"
            )

        proposal = ExternalEvaluatorProposal(
            manuscript_id=manuscript_id,
            proposed_by_id=proposed_by_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            status="proposed",
        )
        self.db.add(proposal)
        await self.db.commit()
        await self.db.refresh(proposal)

        logger.info(
            f"External evaluator proposed ({data.email}) for manuscript {manuscript_id} "
            f"by internal evaluator {proposed_by_id}"
        )
        return proposal

    async def list_proposals(self, manuscript_id: int) -> List[ExternalEvaluatorProposal]:
        """Liste les propositions d'un manuscrit (consultable par l'éditeur et l'interne)."""
        result = await self.db.execute(
            select(ExternalEvaluatorProposal)
            .where(ExternalEvaluatorProposal.manuscript_id == manuscript_id)
            .order_by(ExternalEvaluatorProposal.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_proposal(
        self,
        manuscript_id: int,
        proposal_id: int,
        user_id: int,
    ) -> dict:
        """Supprime une proposition (réservé à l'évaluateur interne du manuscrit)."""
        proposal = await self.db.get(ExternalEvaluatorProposal, proposal_id)
        if not proposal or proposal.manuscript_id != manuscript_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proposal not found"
            )

        await self._ensure_internal_evaluator(manuscript_id, user_id)

        await self.db.delete(proposal)
        await self.db.commit()
        return {"message": "Proposal deleted", "proposalId": proposal_id}