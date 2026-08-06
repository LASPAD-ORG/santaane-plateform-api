"""
Service layer for evaluator assignment management
"""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.models.language import Language
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
from app.models.manuscript import Manuscript
from app.models.user import User
from app.models.user_role import UserRole
from app.models.enums import EvaluatorAssignmentStatus, EvaluatorKind
from app.models.manuscript_evaluation_grid import ManuscriptEvaluationGrid
from app.core.email import EmailService
from app.core.logging import logger


class EvaluatorAssignmentService:
    """Service for managing evaluator assignments"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_evaluator(
        self,
        manuscript_id: int,
        evaluator_id: int,
        evaluation_deadline: datetime,
        assigned_by_id: int,
        kind: str = EvaluatorKind.EXTERNAL.value,
    ) -> dict:
        """Assign an evaluator to a manuscript and send notification email.

        kind='external' (défaut) ou 'internal' (pré-examen interne).
        """

        manuscript_result = await self.db.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        manuscript = manuscript_result.scalar_one_or_none()
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manuscript with ID {manuscript_id} not found"
            )

        # Gate 1 : anonymisation requise dans tous les cas
        if not manuscript.is_anonymized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign evaluator: manuscript must be anonymized first"
            )

        # Gate 2 : un évaluateur EXTERNE exige la validation interne préalable
        if kind == EvaluatorKind.EXTERNAL.value and not manuscript.is_internally_validated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign external evaluator: manuscript must be internally validated first"
            )

        evaluator_result = await self.db.execute(
            select(User).where(User.id == evaluator_id)
        )
        evaluator = evaluator_result.scalar_one_or_none()
        if not evaluator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluator with ID {evaluator_id} not found"
            )

        existing_assignment = await self.db.execute(
            select(ManuscriptEvaluatorLink).where(
                ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
                ManuscriptEvaluatorLink.evaluator_id == evaluator_id
            )
        )
        if existing_assignment.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This evaluator is already assigned to this manuscript"
            )

        if evaluation_deadline.tzinfo is not None:
            evaluation_deadline = evaluation_deadline.replace(tzinfo=None)

        assignment = ManuscriptEvaluatorLink(
            manuscript_id=manuscript_id,
            evaluator_id=evaluator_id,
            assigned_by_id=assigned_by_id,
            status=EvaluatorAssignmentStatus.PENDING,
            kind=kind,
            evaluation_deadline=evaluation_deadline
        )

        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)

        pdf_url = f"https://santaane.mansatoulo.fr/uploads/{manuscript.pdf_filename}"
        deadline_str = evaluation_deadline.strftime("%d/%m/%Y")

        language_result = await self.db.execute(
            select(Language).where(Language.id == manuscript.language_id)
        )
        language = language_result.scalar_one_or_none()
        manuscript_lang = language.code if language else 'fr'

        email_sent = EmailService.send_evaluation_request_email(
            to_email=evaluator.email,
            evaluator_name=evaluator.full_name,
            manuscript_title=manuscript.title,
            manuscript_pdf_url=pdf_url,
            evaluation_deadline=deadline_str,
            lang=manuscript_lang
        )

        try:
            EmailService.send_request_evaluation(
                to_email="laspad-plateform@hamadouba.com",
                evaluator_name=evaluator.full_name,
                manuscript_title=manuscript.title,
                manuscript_id=manuscript.id,
                assignment_deadline=deadline_str,
                lang=manuscript_lang
            )
            logger.info(f"System notification sent for evaluator assignment to manuscript {manuscript_id}")
        except Exception as e:
            logger.error(f"Failed to send system notification for evaluator assignment: {str(e)}")

        try:
            author_result = await self.db.execute(
                select(User).where(User.id == manuscript.author_id)
            )
            author = author_result.scalar_one_or_none()

            if author:
                # [Retire sur demande metier] Pas de notification a l'auteur lors de l'assignation d'un evaluateur.
                # L'auteur voit le statut sur la plateforme.
                pass
        except Exception as e:
            logger.error(f"Failed to send author notification for evaluator assignment: {str(e)}")

        if not email_sent:
            logger.warning(f"Failed to send evaluation request email to {evaluator.email}")

        return {
            "message": "Evaluator assigned successfully",
            "assignment": {
                "manuscriptId": manuscript_id,
                "evaluatorId": evaluator_id,
                "evaluatorName": evaluator.full_name,
                "evaluatorEmail": evaluator.email,
                "assignedById": assigned_by_id,
                "assignedAt": assignment.assigned_at,
                "status": assignment.status,
                "kind": assignment.kind,
                "evaluationDeadline": assignment.evaluation_deadline
            }
        }

    async def respond_to_assignment(
        self,
        manuscript_id: int,
        evaluator_id: int,
        accept: bool
    ) -> dict:
        """Evaluator accepts or declines an assignment"""

        result = await self.db.execute(
            select(ManuscriptEvaluatorLink).where(
                ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
                ManuscriptEvaluatorLink.evaluator_id == evaluator_id
            )
        )
        assignment = result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        if assignment.status != EvaluatorAssignmentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Assignment already {assignment.status.value}"
            )

        manuscript_result = await self.db.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        manuscript = manuscript_result.scalar_one_or_none()

        evaluator_result = await self.db.execute(
            select(User).where(User.id == evaluator_id)
        )
        evaluator = evaluator_result.scalar_one_or_none()

        if accept:
            assignment.status = EvaluatorAssignmentStatus.ACCEPTED
            assignment.response_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.commit()

            language_result = await self.db.execute(
                select(Language).where(Language.id == manuscript.language_id)
            )
            language = language_result.scalar_one_or_none()
            manuscript_lang = language.code if language else 'fr'

            try:
                # Notification système
                EmailService.send_evaluator_response_notification(
                    manuscript_id=manuscript_id,
                    manuscript_title=manuscript.title if manuscript else f"Manuscrit #{manuscript_id}",
                    evaluator_name=evaluator.full_name if evaluator else "Évaluateur",
                    evaluator_email=evaluator.email if evaluator else "",
                    response="accepted",
                    lang=manuscript_lang
                )
                logger.info(f"Evaluator acceptance notification sent for manuscript {manuscript_id} in {manuscript_lang}")

                # Notification auteur
                if manuscript and evaluator:
                    try:
                        author_result = await self.db.execute(
                            select(User).where(User.id == manuscript.author_id)
                        )
                        author = author_result.scalar_one_or_none()
                        if author:
                            # [Retire sur demande metier] Pas de notification a l'auteur quand l'evaluateur accepte.
                            # L'auteur voit "en cours d'evaluation" sur la plateforme.
                            pass
                    except Exception as e:
                        logger.error(f"Failed to send author notification for evaluator acceptance: {str(e)}")

                # Notification éditeurs
                try:
                    editors_result = await self.db.execute(
                        select(User)
                        .join(UserRole, UserRole.user_id == User.id)
                        .where(UserRole.role_id == 2)
                        .where(User.is_active == True)
                    )
                    editors = editors_result.scalars().all()
                    for editor in editors:
                        if editor.email:
                            EmailService.send_email(
                                to_email=editor.email,
                                subject=f"Évaluateur a accepté - {manuscript.title[:50] if manuscript else ''}...",
                                body=EmailService._get_base_template(
                                    "Demande d'évaluation acceptée",
                                    f"""<div style="color:#333;">
                                    <p>L'évaluateur <strong>{evaluator.full_name if evaluator else 'Évaluateur'}</strong> a <strong style="color:#59a498;">accepté</strong> d'évaluer le manuscrit :</p>
                                    <div style="background:#f8f9fa;border-left:4px solid #59a498;padding:20px;border-radius:8px;margin:25px 0;">
                                        <h3 style="margin:0;color:#59a498;">"{manuscript.title if manuscript else ''}"</h3>
                                        <p style="margin:10px 0 0 0;font-size:14px;color:#666;">ID : #{manuscript_id}</p>
                                    </div>
                                    <div style="text-align:center;margin:35px 0;">
                                        <a href="https://www.globalafricajournal.org/dashboard/editor/manuscripts/{manuscript_id}"
                                           style="display:inline-block;padding:15px 40px;background:linear-gradient(135deg,#59a498 0%,#4a8a7f 100%);color:#fff;text-decoration:none;border-radius:8px;font-size:16px;font-weight:600;">
                                            Voir le manuscrit
                                        </a>
                                    </div></div>"""
                                )
                            )
                    logger.info(f"Notifications envoyées à {len(editors)} éditeur(s) (accept)")
                except Exception as e:
                    logger.error(f"Erreur notification éditeurs (accept): {str(e)}")

            except Exception as e:
                logger.error(f"Failed to send evaluator acceptance notifications: {str(e)}")

            return {
                "message": "Assignment accepted successfully",
                "status": "accepted"
            }
        else:
            await self.db.delete(assignment)
            await self.db.commit()

            language_result = await self.db.execute(
                select(Language).where(Language.id == manuscript.language_id)
            )
            language = language_result.scalar_one_or_none()
            manuscript_lang = language.code if language else 'fr'

            try:
                # Notification système
                EmailService.send_evaluator_response_notification(
                    manuscript_id=manuscript_id,
                    manuscript_title=manuscript.title if manuscript else f"Manuscrit #{manuscript_id}",
                    evaluator_name=evaluator.full_name if evaluator else "Évaluateur",
                    evaluator_email=evaluator.email if evaluator else "",
                    response="declined",
                    lang=manuscript_lang
                )
                logger.info(f"Evaluator decline notification sent for manuscript {manuscript_id} in {manuscript_lang}")

                # Notification auteur
                if manuscript and evaluator:
                    try:
                        author_result = await self.db.execute(
                            select(User).where(User.id == manuscript.author_id)
                        )
                        author = author_result.scalar_one_or_none()
                        if author:
                            # [Retire sur demande metier] Pas de notification a l'auteur quand l'evaluateur refuse.
                            pass
                    except Exception as e:
                        logger.error(f"Failed to send author notification for evaluator decline: {str(e)}")

                # Notification éditeurs
                try:
                    editors_result = await self.db.execute(
                        select(User)
                        .join(UserRole, UserRole.user_id == User.id)
                        .where(UserRole.role_id == 2)
                        .where(User.is_active == True)
                    )
                    editors = editors_result.scalars().all()
                    for editor in editors:
                        if editor.email:
                            EmailService.send_email(
                                to_email=editor.email,
                                subject=f"Évaluateur a refusé - {manuscript.title[:50] if manuscript else ''}...",
                                body=EmailService._get_base_template(
                                    "Demande d'évaluation refusée",
                                    f"""<div style="color:#333;">
                                    <p>L'évaluateur <strong>{evaluator.full_name if evaluator else 'Évaluateur'}</strong> a <strong style="color:#dc3545;">refusé</strong> d'évaluer le manuscrit :</p>
                                    <div style="background:#f8f9fa;border-left:4px solid #dc3545;padding:20px;border-radius:8px;margin:25px 0;">
                                        <h3 style="margin:0;color:#dc3545;">"{manuscript.title if manuscript else ''}"</h3>
                                        <p style="margin:10px 0 0 0;font-size:14px;color:#666;">ID : #{manuscript_id}</p>
                                    </div>
                                    <div style="background:#fff3cd;border-left:4px solid #ffc107;padding:15px;border-radius:8px;margin:25px 0;">
                                        <p style="margin:0;font-size:14px;color:#856404;"><strong>Action requise :</strong> Veuillez assigner un nouvel évaluateur.</p>
                                    </div>
                                    <div style="text-align:center;margin:35px 0;">
                                        <a href="https://www.globalafricajournal.org/dashboard/editor/manuscripts/{manuscript_id}"
                                           style="display:inline-block;padding:15px 40px;background:linear-gradient(135deg,#59a498 0%,#4a8a7f 100%);color:#fff;text-decoration:none;border-radius:8px;font-size:16px;font-weight:600;">
                                            Assigner un évaluateur
                                        </a>
                                    </div></div>"""
                                )
                            )
                    logger.info(f"Notifications envoyées à {len(editors)} éditeur(s) (decline)")
                except Exception as e:
                    logger.error(f"Erreur notification éditeurs (decline): {str(e)}")

            except Exception as e:
                logger.error(f"Failed to send evaluator decline notifications: {str(e)}")

            return {
                "message": "Assignment declined and removed",
                "status": "declined"
            }

    async def validate_internally(
        self,
        manuscript_id: int,
        internal_evaluator_id: int,
    ) -> dict:
        """L'évaluateur interne valide le manuscrit pour évaluation externe.

        Prérequis : lien interne ACCEPTED + grille d'évaluation soumise.
        Effet : passe is_internally_validated à True, ce qui débloque
        l'assignation d'évaluateurs externes.
        """
        manuscript = await self.db.get(Manuscript, manuscript_id)
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manuscript with ID {manuscript_id} not found"
            )

        # Le demandeur doit être l'évaluateur interne (lien kind='internal')
        link_result = await self.db.execute(
            select(ManuscriptEvaluatorLink).where(
                ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
                ManuscriptEvaluatorLink.evaluator_id == internal_evaluator_id,
                ManuscriptEvaluatorLink.kind == EvaluatorKind.INTERNAL.value,
            )
        )
        link = link_result.scalar_one_or_none()
        if not link:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the internal evaluator of this manuscript"
            )
        if link.status != EvaluatorAssignmentStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must accept the assignment before validating"
            )

        # La grille interne doit être soumise
        grid_result = await self.db.execute(
            select(ManuscriptEvaluationGrid).where(
                ManuscriptEvaluationGrid.manuscript_id == manuscript_id,
                ManuscriptEvaluationGrid.evaluator_id == internal_evaluator_id,
                ManuscriptEvaluationGrid.submitted_at.isnot(None),
            )
        )
        if not grid_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must submit your evaluation grid before validating"
            )

        if manuscript.is_internally_validated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manuscript already internally validated"
            )

        manuscript.is_internally_validated = True
        manuscript.internally_validated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        manuscript.internally_validated_by_id = internal_evaluator_id
        self.db.add(manuscript)
        await self.db.commit()
        await self.db.refresh(manuscript)

        # Notifier les éditeurs que le manuscrit est prêt pour l'évaluation externe
        try:
            evaluator_result = await self.db.execute(
                select(User).where(User.id == internal_evaluator_id)
            )
            internal_evaluator = evaluator_result.scalar_one_or_none()
            internal_name = internal_evaluator.full_name if internal_evaluator else "Évaluateur interne"

            editors_result = await self.db.execute(
                select(User)
                .join(UserRole, UserRole.user_id == User.id)
                .where(UserRole.role_id == 2)
                .where(User.is_active == True)
            )
            editors = editors_result.scalars().all()
            for editor in editors:
                if editor.email:
                    EmailService.send_email(
                        to_email=editor.email,
                        subject=f"Validation interne - {manuscript.title[:50]}...",
                        body=EmailService._get_base_template(
                            "Manuscrit validé pour évaluation externe",
                            f"""<div style="color:#333;">
                            <p>L'évaluateur interne <strong>{internal_name}</strong> a <strong style="color:#59a498;">validé</strong> le manuscrit pour l'évaluation externe :</p>
                            <div style="background:#f8f9fa;border-left:4px solid #59a498;padding:20px;border-radius:8px;margin:25px 0;">
                                <h3 style="margin:0;color:#59a498;">"{manuscript.title}"</h3>
                                <p style="margin:10px 0 0 0;font-size:14px;color:#666;">ID : #{manuscript_id}</p>
                            </div>
                            <p>Vous pouvez maintenant assigner des évaluateurs externes.</p>
                            <div style="text-align:center;margin:35px 0;">
                                <a href="https://www.globalafricajournal.org/dashboard/editor/manuscripts/{manuscript_id}"
                                   style="display:inline-block;padding:15px 40px;background:linear-gradient(135deg,#59a498 0%,#4a8a7f 100%);color:#fff;text-decoration:none;border-radius:8px;font-size:16px;font-weight:600;">
                                    Assigner des évaluateurs externes
                                </a>
                            </div></div>"""
                        )
                    )
            logger.info(f"Internal validation notification sent to {len(editors)} editor(s) for manuscript {manuscript_id}")
        except Exception as e:
            logger.error(f"Failed to send internal validation notification: {str(e)}")

        return {
            "message": "Manuscript internally validated. External evaluators can now be assigned.",
            "manuscriptId": manuscript_id,
            "internallyValidatedAt": manuscript.internally_validated_at,
        }

    async def send_reminder_email(
        self,
        manuscript_id: int,
        evaluator_id: int
    ) -> dict:
        """Send reminder email to evaluator who hasn't responded"""

        result = await self.db.execute(
            select(ManuscriptEvaluatorLink).where(
                ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
                ManuscriptEvaluatorLink.evaluator_id == evaluator_id
            )
        )
        assignment = result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        if assignment.status != EvaluatorAssignmentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot send reminder: assignment status is {assignment.status.value}"
            )

        manuscript_result = await self.db.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        manuscript = manuscript_result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manuscript with ID {manuscript_id} not found"
            )

        evaluator_result = await self.db.execute(
            select(User).where(User.id == evaluator_id)
        )
        evaluator = evaluator_result.scalar_one_or_none()

        if not evaluator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluator with ID {evaluator_id} not found"
            )

        deadline_str = assignment.evaluation_deadline.strftime("%d/%m/%Y")

        language_result = await self.db.execute(
            select(Language).where(Language.id == manuscript.language_id)
        )
        language = language_result.scalar_one_or_none()
        language_code = language.code.lower() if language else 'fr'

        email_sent = EmailService.send_evaluation_reminder_email(
            to_email=evaluator.email,
            evaluator_name=evaluator.full_name,
            manuscript_title=manuscript.title,
            evaluation_deadline=deadline_str,
            lang=language_code
        )

        try:
            author_result = await self.db.execute(
                select(User).where(User.id == manuscript.author_id)
            )
            author = author_result.scalar_one_or_none()

            if author:
                days_remaining = (assignment.evaluation_deadline - datetime.now(timezone.utc).replace(tzinfo=None)).days
                days_remaining = max(0, days_remaining)

                EmailService.send_autor_reminder_evalutor(
                    to_email=author.email,
                    author_name=author.full_name,
                    manuscript_title=manuscript.title,
                    days_remaining=days_remaining,
                    lang=language_code
                )
                logger.info(f"Author notification sent for evaluator reminder for manuscript {manuscript_id}")
        except Exception as e:
            logger.error(f"Failed to send author notification for evaluator reminder: {str(e)}")

        if not email_sent:
            logger.warning(f"Failed to send reminder email to {evaluator.email}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send reminder email"
            )

        logger.info(f"Reminder email sent to {evaluator.email} for manuscript {manuscript_id}")

        return {
            "message": "Reminder email sent successfully",
            "evaluatorEmail": evaluator.email,
            "manuscriptTitle": manuscript.title
        }