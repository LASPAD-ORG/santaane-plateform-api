"""
Service for managing manuscript annotations
"""
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
import uuid
from app.models.manuscript_annotation import ManuscriptAnnotation
from app.models.manuscript_evaluator_link import ManuscriptEvaluatorLink
from app.models.manuscript import Manuscript
from app.models.user import User
from app.models.enums import EvaluatorAssignmentStatus
from app.modules.manuscripts.annotation_schemas import AnnotationCreate, AnnotationUpdate, AnnotationResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


class AnnotationService:
    """Service for managing manuscript annotations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_annotation(
        self,
        manuscript_id: int,
        evaluator_id: int,
        data: AnnotationCreate
    ) -> AnnotationResponse:
        """
        Create a new annotation on a manuscript.
        Only evaluators who have ACCEPTED the assignment can annotate.
        """
        logger.info(f"Creating annotation for manuscript {manuscript_id} by evaluator {evaluator_id}")

        # Check if evaluator is assigned and has accepted
        assignment_query = select(ManuscriptEvaluatorLink).where(
            ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
            ManuscriptEvaluatorLink.evaluator_id == evaluator_id
        )
        assignment_result = await self.db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this manuscript"
            )

        if assignment.status != EvaluatorAssignmentStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must accept the evaluation assignment before annotating"
            )

        # Create annotation
        annotation = ManuscriptAnnotation(
            id=str(uuid.uuid4()),
            manuscript_id=manuscript_id,
            evaluator_id=evaluator_id,
            annotation_type=data.annotationType,
            page_number=data.pageNumber,
            x_position=data.xPosition,
            y_position=data.yPosition,
            position_data=data.positionData,
            comment=data.comment,
            content_data=data.contentData
        )

        self.db.add(annotation)
        await self.db.commit()
        await self.db.refresh(annotation)

        # Load evaluator info
        evaluator_query = select(User).where(User.id == evaluator_id)
        evaluator_result = await self.db.execute(evaluator_query)
        evaluator = evaluator_result.scalar_one()

        logger.info(f"Annotation {annotation.id} created successfully")

        return AnnotationResponse(
            id=annotation.id,
            manuscriptId=annotation.manuscript_id,
            evaluatorId=annotation.evaluator_id,
            evaluatorName=evaluator.full_name,
            annotationType=annotation.annotation_type,
            pageNumber=annotation.page_number,
            xPosition=annotation.x_position,
            yPosition=annotation.y_position,
            positionData=annotation.position_data,
            comment=annotation.comment,
            contentData=annotation.content_data,
            createdAt=annotation.created_at,
            updatedAt=annotation.updated_at
        )

    async def get_manuscript_annotations(
        self,
        manuscript_id: int,
        evaluator_id: int
    ) -> List[AnnotationResponse]:
        """
        Get all annotations for a manuscript.
        Evaluators can only see their own annotations.
        IMPORTANT: NEVER return REDACTION type to evaluators.
        """
        logger.info(f"Fetching annotations for manuscript {manuscript_id} by evaluator {evaluator_id}")

        # Verify evaluator is assigned
        assignment_query = select(ManuscriptEvaluatorLink).where(
            ManuscriptEvaluatorLink.manuscript_id == manuscript_id,
            ManuscriptEvaluatorLink.evaluator_id == evaluator_id
        )
        assignment_result = await self.db.execute(assignment_query)
        assignment = assignment_result.scalar_one_or_none()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to this manuscript"
            )

        # Get annotations - EXCLUDE REDACTION type
        query = (
            select(ManuscriptAnnotation)
            .where(
                ManuscriptAnnotation.manuscript_id == manuscript_id,
                ManuscriptAnnotation.evaluator_id == evaluator_id,
                ManuscriptAnnotation.annotation_type != "redaction"  # CRITICAL: Never expose redactions
            )
            .options(selectinload(ManuscriptAnnotation.evaluator))
            .order_by(ManuscriptAnnotation.page_number, ManuscriptAnnotation.created_at)
        )

        result = await self.db.execute(query)
        annotations = result.scalars().all()

        return [
            AnnotationResponse(
                id=ann.id,
                manuscriptId=ann.manuscript_id,
                evaluatorId=ann.evaluator_id,
                evaluatorName=ann.evaluator.full_name,
                annotationType=ann.annotation_type,
                pageNumber=ann.page_number,
                xPosition=ann.x_position,
                yPosition=ann.y_position,
                positionData=ann.position_data,
                comment=ann.comment,
                contentData=ann.content_data,
                createdAt=ann.created_at,
                updatedAt=ann.updated_at
            )
            for ann in annotations
        ]

    async def update_annotation(
        self,
        annotation_id: str,
        evaluator_id: int,
        data: AnnotationUpdate
    ) -> AnnotationResponse:
        """Update an annotation. Only the creator can update their annotation."""
        logger.info(f"Updating annotation {annotation_id}")

        # Get annotation
        query = (
            select(ManuscriptAnnotation)
            .where(ManuscriptAnnotation.id == annotation_id)
            .options(selectinload(ManuscriptAnnotation.evaluator))
        )
        result = await self.db.execute(query)
        annotation = result.scalar_one_or_none()

        if not annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Annotation not found"
            )

        if annotation.evaluator_id != evaluator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own annotations"
            )

        # Update
        annotation.comment = data.comment
        annotation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(annotation)

        return AnnotationResponse(
            id=annotation.id,
            manuscriptId=annotation.manuscript_id,
            evaluatorId=annotation.evaluator_id,
            evaluatorName=annotation.evaluator.full_name,
            annotationType=annotation.annotation_type,
            pageNumber=annotation.page_number,
            xPosition=annotation.x_position,
            yPosition=annotation.y_position,
            positionData=annotation.position_data,
            comment=annotation.comment,
            contentData=annotation.content_data,
            createdAt=annotation.created_at,
            updatedAt=annotation.updated_at
        )

    async def delete_annotation(
        self,
        annotation_id: str,
        evaluator_id: int
    ) -> dict:
        """Delete an annotation. Only the creator can delete their annotation."""
        logger.info(f"Deleting annotation {annotation_id}")

        # Get annotation
        query = select(ManuscriptAnnotation).where(ManuscriptAnnotation.id == annotation_id)
        result = await self.db.execute(query)
        annotation = result.scalar_one_or_none()

        if not annotation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Annotation not found"
            )

        if annotation.evaluator_id != evaluator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own annotations"
            )

        await self.db.delete(annotation)
        await self.db.commit()

        logger.info(f"Annotation {annotation_id} deleted successfully")
        return {"message": "Annotation deleted successfully"}
