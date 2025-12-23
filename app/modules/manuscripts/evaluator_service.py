"""
Service layer for evaluator assignment management
"""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
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
        """Assign an evaluator to a manuscript and send notification email"""
        
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
        pdf_url = f"http://localhost:3000/uploads/{manuscript.pdf_filename}"
        
        # Format deadline for email
        deadline_str = evaluation_deadline.strftime("%d %B %Y")
        
        # Send evaluation request email
        email_sent = EmailService.send_evaluation_request_email(
            to_email=evaluator.email,
            evaluator_name=evaluator.full_name,
            manuscript_title=manuscript.title,
            manuscript_pdf_url=pdf_url,
            evaluation_deadline=deadline_str
        )
        
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
        
        if accept:
            # Accept assignment
            assignment.status = EvaluatorAssignmentStatus.ACCEPTED
            assignment.response_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self.db.commit()
            
            return {
                "message": "Assignment accepted successfully",
                "status": "accepted"
            }
        else:
            # Decline and delete assignment
            await self.db.delete(assignment)
            await self.db.commit()
            
            return {
                "message": "Assignment declined and removed",
                "status": "declined"
            }
