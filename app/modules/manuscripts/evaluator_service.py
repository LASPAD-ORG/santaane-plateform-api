"""
Service layer for evaluator assignment management
"""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from sqlalchemy import select
from app.models.language import Language
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
from app.models.manuscript import Manuscript
from app.models.user import User
from app.models.enums import EvaluatorAssignmentStatus
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
        assigned_by_id: int
     ) -> dict:
        """Asaccsign an evaluator to a manuscript and send notification email"""
        
        # Check if manuscript exists
        manuscript_result = await self.db.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        manuscript = manuscript_result.scalar_one_or_none()
        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Manuscript with ID {manuscript_id} not found"
            )

        # CRITICAL: Verify that manuscript is anonymized before allowing assignment
        if not manuscript.is_anonymized:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign evaluator: manuscript must be anonymized first"
            )

        # Check if evaluator exists and has EVALUATOR role (role_id = 3)
        evaluator_result = await self.db.execute(
            select(User).where(User.id == evaluator_id)
        )
        evaluator = evaluator_result.scalar_one_or_none()
        if not evaluator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evaluator with ID {evaluator_id} not found"
            )
        
        # Check if already assigned
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
        
        # Create assignment
        # Remove timezone from evaluation_deadline to match database TIMESTAMP WITHOUT TIME ZONE
        if evaluation_deadline.tzinfo is not None:
            evaluation_deadline = evaluation_deadline.replace(tzinfo=None)
        
        assignment = ManuscriptEvaluatorLink(
            manuscript_id=manuscript_id,
            evaluator_id=evaluator_id,
            assigned_by_id=assigned_by_id,
            status=EvaluatorAssignmentStatus.PENDING,
            evaluation_deadline=evaluation_deadline
        )
        
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        
        # Generate PDF URL (using uploads directory path)
        pdf_url = f"https://santaane.mansatoulo.fr/uploads/{manuscript.pdf_filename}"
        
        # Format deadline for email (French format: jj/mm/aaaa)
        deadline_str = evaluation_deadline.strftime("%d/%m/%Y")
        
        # Get manuscript language for email
        language_result = await self.db.execute(
            select(Language).where(Language.id == manuscript.language_id)
        )
        language = language_result.scalar_one_or_none()
        manuscript_lang = language.code if language else 'fr'
        
        # Send evaluation request email to evaluator
        email_sent = EmailService.send_evaluation_request_email(
            to_email=evaluator.email,
            evaluator_name=evaluator.full_name,
            manuscript_title=manuscript.title,
            manuscript_pdf_url=pdf_url,
            evaluation_deadline=deadline_str,
            lang=manuscript_lang
        )
        
        # Send notification to system about evaluator assignment
        try:
            EmailService.send_request_evaluation(
                to_email="laspad-plateform@hamadouba.com",  # Email système
                evaluator_name=evaluator.full_name,
                manuscript_title=manuscript.title,
                manuscript_id=manuscript.id,
                assignment_deadline=deadline_str,
                lang=manuscript_lang
            )
            logger.info(f"System notification sent for evaluator assignment to manuscript {manuscript_id}")
        except Exception as e:
            logger.error(f"Failed to send system notification for evaluator assignment: {str(e)}")
            # Don't fail the whole operation if notification fails
        
        # Send notification to author about evaluator assignment
        try:
            # Get author details
            author_result = await self.db.execute(
                select(User).where(User.id == manuscript.author_id)
            )
            author = author_result.scalar_one_or_none()
            
            if author:
                # Envoyer la notification à l'auteur (sans révéler l'identité de l'évaluateur)
                EmailService.send_autor_manuscript_assigner_a_evaluator(
                    to_email=author.email,
                    author_name=author.full_name,
                    manuscript_title=manuscript.title,
                    manuscript_id=manuscript.id,
                    lang=manuscript_lang
                )
                logger.info(f"Author notification sent for evaluator assignment to manuscript {manuscript_id}")
        except Exception as e:
            logger.error(f"Failed to send author notification for evaluator assignment: {str(e)}")
            # Don't fail the whole operation if notification fails
        
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
        
        # Get assignment
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
        
        # Get manuscript and evaluator details for email notification
        manuscript_result = await self.db.execute(
            select(Manuscript).where(Manuscript.id == manuscript_id)
        )
        manuscript = manuscript_result.scalar_one_or_none()
        
        evaluator_result = await self.db.execute(
            select(User).where(User.id == evaluator_id)
        )
        evaluator = evaluator_result.scalar_one_or_none()
        
        if accept:
            # Accept assignment
            assignment.status = EvaluatorAssignmentStatus.ACCEPTED
            assignment.response_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.commit()
            
            # Get manuscript language for notifications
            language_result = await self.db.execute(
                select(Language).where(Language.id == manuscript.language_id)
            )
            language = language_result.scalar_one_or_none()
            manuscript_lang = language.code if language else 'fr'
            
            # Send notification to system
            try:
                EmailService.send_evaluator_response_notification(
                    manuscript_id=manuscript_id,
                    manuscript_title=manuscript.title if manuscript else f"Manuscrit #{manuscript_id}",
                    evaluator_name=evaluator.full_name if evaluator else "Évaluateur",
                    evaluator_email=evaluator.email if evaluator else "",
                    response="accepted",
                    lang=manuscript_lang
                )
                logger.info(f"Evaluator acceptance notification sent for manuscript {manuscript_id} in {manuscript_lang}")
                
                # Send notification to author about evaluator's acceptance
                if manuscript and evaluator:
                    try:
                        author_result = await self.db.execute(
                            select(User).where(User.id == manuscript.author_id)
                        )
                        author = author_result.scalar_one_or_none()
                        
                        if author:
                            # Notifier l'auteur de l'acceptation (sans révéler l'identité de l'évaluateur)
                            EmailService.send_autor_reponse_evalutor_to_assignation(
                                to_email=author.email,
                                author_name=author.full_name,
                                manuscript_title=manuscript.title,
                                manuscript_id=manuscript.id,
                                accepted=True,
                                lang=manuscript_lang
                            )
                            logger.info(f"Author notification sent for evaluator acceptance of manuscript {manuscript_id}")
                    except Exception as e:
                        logger.error(f"Failed to send author notification for evaluator acceptance: {str(e)}")
            except Exception as e:
                logger.error(f"Failed to send evaluator acceptance notifications: {str(e)}")
            
            return {
                "message": "Assignment accepted successfully",
                "status": "accepted"
            }
        else:
            # Decline and delete assignment
            await self.db.delete(assignment)
            await self.db.commit()
            
            # Get manuscript language for notifications
            language_result = await self.db.execute(
                select(Language).where(Language.id == manuscript.language_id)
            )
            language = language_result.scalar_one_or_none()
            manuscript_lang = language.code if language else 'fr'
            
            # Send notification to system
            try:
                EmailService.send_evaluator_response_notification(
                    manuscript_id=manuscript_id,
                    manuscript_title=manuscript.title if manuscript else f"Manuscrit #{manuscript_id}",
                    evaluator_name=evaluator.full_name if evaluator else "Évaluateur",
                    evaluator_email=evaluator.email if evaluator else "",
                    response="declined",
                    lang=manuscript_lang
                )
                logger.info(f"Evaluator decline notification sent for manuscript {manuscript_id} in {manuscript_lang}")
                
                # Send notification to author about evaluator's decline
                if manuscript and evaluator:
                    try:
                        author_result = await self.db.execute(
                            select(User).where(User.id == manuscript.author_id)
                        )
                        author = author_result.scalar_one_or_none()
                        
                        if author:
                            # Notifier l'auteur du refus (sans révéler l'identité de l'évaluateur)
                            EmailService.send_autor_reponse_evalutor_to_assignation(
                                to_email=author.email,
                                author_name=author.full_name,
                                manuscript_title=manuscript.title,
                                manuscript_id=manuscript.id,
                                accepted=False,
                                lang=manuscript_lang
                            )
                            logger.info(f"Author notification sent for evaluator decline of manuscript {manuscript_id}")
                    except Exception as e:
                        logger.error(f"Failed to send author notification for evaluator decline: {str(e)}")
            except Exception as e:
                logger.error(f"Failed to send evaluator decline notifications: {str(e)}")
            
            return {
                "message": "Assignment declined and removed",
                "status": "declined"
            }

    async def send_reminder_email(
        self,
        manuscript_id: int,
        evaluator_id: int
     ) -> dict:
        """Send reminder email to evaluator who hasn't responded"""

        # Get assignment
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

        # Only send reminder if status is PENDING
        if assignment.status != EvaluatorAssignmentStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot send reminder: assignment status is {assignment.status.value}"
            )

        # Get manuscript and evaluator details
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

        # Format deadline for email (French format: jj/mm/aaaa)
        deadline_str = assignment.evaluation_deadline.strftime("%d/%m/%Y")
        
        # Get manuscript language for email
        language_result = await self.db.execute(
            select(Language).where(Language.id == manuscript.language_id)
        )
        language = language_result.scalar_one_or_none()
        language_code = language.code.lower() if language else 'fr'

        # Send reminder email to evaluator
        email_sent = EmailService.send_evaluation_reminder_email(
            to_email=evaluator.email,
            evaluator_name=evaluator.full_name,
            manuscript_title=manuscript.title,
            evaluation_deadline=deadline_str,
            lang=language_code
        )
        
        # Send notification to author about reminder
        try:
            # Get author details
            author_result = await self.db.execute(
                select(User).where(User.id == manuscript.author_id)
            )
            author = author_result.scalar_one_or_none()
            
            if author:
                # Calculate days remaining until deadline
                days_remaining = (assignment.evaluation_deadline - datetime.now(timezone.utc).replace(tzinfo=None)).days
                days_remaining = max(0, days_remaining)  # Ensure it's not negative
                
                # Envoyer un rappel à l'auteur (sans révéler l'identité de l'évaluateur)
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
            # Don't fail the whole operation if notification fails

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
