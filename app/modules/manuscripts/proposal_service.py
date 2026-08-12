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
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role
from app.models.language import Language
from app.models.enums import EvaluatorAssignmentStatus
from app.core.security import hash_password
from app.core.email import EmailService
from datetime import datetime


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

    async def list_proposals(self, manuscript_id: int) -> list:
        """Liste enrichie des propositions : proposeur (interne) + statut de compte.

        Retourne des dictionnaires (serialises via ProposalEnrichedResponse).
        """
        EVALUATOR_ROLE_NAME = "EVALUATOR"

        result = await self.db.execute(
            select(ExternalEvaluatorProposal)
            .where(ExternalEvaluatorProposal.manuscript_id == manuscript_id)
            .order_by(ExternalEvaluatorProposal.created_at.desc())
        )
        proposals = list(result.scalars().all())

        enriched = []
        for p in proposals:
            # Nom du proposeur (evaluateur interne)
            proposer = await self.db.get(User, p.proposed_by_id)
            proposed_by_name = proposer.full_name if proposer else None

            # Statut de compte de la personne proposee (par email)
            user_result = await self.db.execute(
                select(User).where(User.email == p.email)
            )
            proposed_user = user_result.scalar_one_or_none()

            has_account = proposed_user is not None
            account_roles = []
            has_evaluator_role = False

            if proposed_user is not None:
                roles_result = await self.db.execute(
                    select(Role.name)
                    .join(UserRole, UserRole.role_id == Role.id)
                    .where(UserRole.user_id == proposed_user.id)
                )
                account_roles = [r for r in roles_result.scalars().all()]
                has_evaluator_role = EVALUATOR_ROLE_NAME in account_roles

            enriched.append({
                "id": p.id,
                "manuscriptId": p.manuscript_id,
                "proposedById": p.proposed_by_id,
                "proposedByName": proposed_by_name,
                "firstName": p.first_name,
                "lastName": p.last_name,
                "email": p.email,
                "status": p.status,
                "createdAt": p.created_at,
                "hasAccount": has_account,
                "accountRoles": account_roles,
                "hasEvaluatorRole": has_evaluator_role,
            })

        return enriched

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
        logger.info(f"Proposal {proposal_id} deleted for manuscript {manuscript_id} by {user_id}")
        return {"message": "Proposal deleted"}

    async def assign_proposed_evaluator(
        self,
        manuscript_id: int,
        proposal_id: int,
        assigned_by_id: int,
        evaluation_deadline: datetime,
    ) -> dict:
        """Affecte un evaluateur externe propose au manuscrit.

        Gere 3 cas :
        - Aucun compte : cree le compte (roles AUTHOR + EVALUATOR, mdp par defaut) + email avec identifiants.
        - Compte sans role EVALUATOR : ajoute le role + email sans identifiants.
        - Compte avec role EVALUATOR : rien a changer + email sans identifiants.
        Puis cree le lien d'evaluation externe (PENDING) et envoie l'invitation.
        """
        EVALUATOR_ROLE_ID = 3
        AUTHOR_ROLE_ID = 4
        DEFAULT_PASSWORD = "GlobalAfrica@2026"

        proposal = await self.db.get(ExternalEvaluatorProposal, proposal_id)
        if not proposal or proposal.manuscript_id != manuscript_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Proposal not found"
            )

        manuscript = await self.db.get(Manuscript, manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manuscript with ID {manuscript_id} not found"
            )

        # Chercher un utilisateur existant par email
        user_result = await self.db.execute(
            select(User).where(User.email == proposal.email)
        )
        user = user_result.scalar_one_or_none()

        account_created = False
        role_added = False
        password_for_email = None

        if user is None:
            # CAS A : creer le compte + roles AUTHOR et EVALUATOR
            full_name = f"{proposal.first_name} {proposal.last_name}".strip()
            user = User(
                email=proposal.email,
                password_hash=hash_password(DEFAULT_PASSWORD),
                full_name=full_name or proposal.email,
                is_active=True,
                email_verified=False,
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

            for role_id in (AUTHOR_ROLE_ID, EVALUATOR_ROLE_ID):
                self.db.add(UserRole(
                    user_id=user.id,
                    role_id=role_id,
                    assigned_by=assigned_by_id,
                ))
            await self.db.commit()

            account_created = True
            password_for_email = DEFAULT_PASSWORD
            logger.info(f"Account created for proposed evaluator {proposal.email} (user {user.id})")
        else:
            # L'utilisateur existe : a-t-il deja le role EVALUATOR ?
            role_result = await self.db.execute(
                select(UserRole).where(
                    UserRole.user_id == user.id,
                    UserRole.role_id == EVALUATOR_ROLE_ID,
                )
            )
            if role_result.scalar_one_or_none() is None:
                # CAS B : ajouter le role EVALUATOR
                self.db.add(UserRole(
                    user_id=user.id,
                    role_id=EVALUATOR_ROLE_ID,
                    assigned_by=assigned_by_id,
                ))
                await self.db.commit()
                role_added = True
                logger.info(f"EVALUATOR role added to existing user {user.id} ({user.email})")
            # CAS C : rien a faire

        # Verifier que le manuscrit est anonymise (garde-fou minimal)
        if not manuscript.is_anonymized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign evaluator: manuscript must be anonymized first"
            )

        # Verifier qu'il n'est pas deja assigne
        existing_link = await self.db.execute(
            select(ManuscriptEvaluatorLink).where(
                ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
                ManuscriptEvaluatorLink.evaluator_id == user.id,
            )
        )
        if existing_link.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This evaluator is already assigned to this manuscript"
            )

        deadline = evaluation_deadline
        if deadline is not None and deadline.tzinfo is not None:
            deadline = deadline.replace(tzinfo=None)

        link = ManuscriptEvaluatorLink(
            manuscript_id=manuscript_id,
            evaluator_id=user.id,
            assigned_by_id=assigned_by_id,
            status=EvaluatorAssignmentStatus.PENDING,
            kind=EvaluatorKind.EXTERNAL.value,
            evaluation_deadline=deadline,
        )
        self.db.add(link)

        # Marquer la proposition comme assignee
        proposal.status = "assigned"
        self.db.add(proposal)
        await self.db.commit()

        # Langue du manuscrit pour l'email
        language = None
        if manuscript.language_id:
            lang_result = await self.db.execute(
                select(Language).where(Language.id == manuscript.language_id)
            )
            language = lang_result.scalar_one_or_none()
        manuscript_lang = language.code if language else "fr"

        deadline_str = deadline.strftime("%d/%m/%Y") if deadline else ""
        roles_label = None
        if account_created:
            roles_label = "Auteur, Evaluateur externe" if manuscript_lang.lower().startswith("fr") else "Author, External reviewer"

        try:
            EmailService.send_external_evaluator_invitation(
                to_email=user.email,
                evaluator_name=user.full_name,
                manuscript_title=manuscript.title,
                evaluation_deadline=deadline_str,
                login_email=user.email,
                password=password_for_email,
                roles=roles_label,
                lang=manuscript_lang,
            )
        except Exception as e:
            logger.error(f"Failed to send external evaluator invitation to {user.email}: {str(e)}")

        logger.info(
            f"Proposed evaluator {user.email} assigned to manuscript {manuscript_id} "
            f"(created={account_created}, role_added={role_added})"
        )
        return {
            "accountCreated": account_created,
            "roleAdded": role_added,
            "assigned": True,
            "evaluatorId": user.id,
            "evaluatorEmail": user.email,
        }
        return {"message": "Proposal deleted", "proposalId": proposal_id}