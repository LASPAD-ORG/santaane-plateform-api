"""
Service for managing manuscript redactions (anonymization)
"""
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
import uuid

from app.models.manuscript_annotation import ManuscriptAnnotation
from app.models.manuscript import Manuscript
from app.models.user import User
from app.modules.manuscripts.redaction_schemas import (
    RedactionCreate,
    RedactionUpdate,
    RedactionResponse,
    AnonymizationStatusRequest,
    AnonymizationStatusResponse
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedactionService:
    """Service for managing manuscript redactions (EDITOR only)"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_redaction(
        self,
        manuscript_id: int,
        editor_id: int,
        data: RedactionCreate
    ) -> RedactionResponse:
        """
        Create a new redaction zone on a manuscript.
        Only EDITOR can create redactions.
        """
        logger.info(f"Creating redaction for manuscript {manuscript_id} by editor {editor_id}")

        # Verify manuscript exists
        manuscript_query = select(Manuscript).where(Manuscript.id == manuscript_id)
        manuscript_result = await self.db.execute(manuscript_query)
        manuscript = manuscript_result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found"
            )

        # Create redaction annotation
        redaction = ManuscriptAnnotation(
            id=str(uuid.uuid4()),
            manuscript_id=manuscript_id,
            evaluator_id=editor_id,  # On réutilise ce champ mais c'est un EDITOR
            annotation_type="redaction",
            page_number=data.pageNumber,
            x_position=data.xPosition,
            y_position=data.yPosition,
            position_data=data.positionData,
            comment=data.comment,
            content_data=data.contentData,
            created_by_role="EDITOR"  # Important: distinguer des annotations EVALUATOR
        )

        self.db.add(redaction)
        await self.db.commit()
        await self.db.refresh(redaction)

        # Load editor info
        editor_query = select(User).where(User.id == editor_id)
        editor_result = await self.db.execute(editor_query)
        editor = editor_result.scalar_one()

        logger.info(f"Redaction {redaction.id} created successfully")

        return RedactionResponse(
            id=redaction.id,
            manuscriptId=redaction.manuscript_id,
            editorId=editor_id,
            editorName=editor.full_name,
            annotationType="redaction",
            pageNumber=redaction.page_number,
            xPosition=redaction.x_position,
            yPosition=redaction.y_position,
            positionData=redaction.position_data,
            comment=redaction.comment,
            contentData=redaction.content_data,
            createdAt=redaction.created_at,
            updatedAt=redaction.updated_at
        )

    async def get_manuscript_redactions(
        self,
        manuscript_id: int,
        editor_id: int
    ) -> List[RedactionResponse]:
        """
        Get all redactions for a manuscript.
        Only EDITOR can see redactions.
        """
        logger.info(f"Fetching redactions for manuscript {manuscript_id}")

        # Verify manuscript exists
        manuscript_query = select(Manuscript).where(Manuscript.id == manuscript_id)
        manuscript_result = await self.db.execute(manuscript_query)
        manuscript = manuscript_result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found"
            )

        # Get all redactions
        query = (
            select(ManuscriptAnnotation)
            .where(
                ManuscriptAnnotation.manuscript_id == manuscript_id,
                ManuscriptAnnotation.annotation_type == "redaction"
            )
            .options(selectinload(ManuscriptAnnotation.evaluator))
            .order_by(ManuscriptAnnotation.page_number, ManuscriptAnnotation.created_at)
        )

        result = await self.db.execute(query)
        redactions = result.scalars().all()

        return [
            RedactionResponse(
                id=red.id,
                manuscriptId=red.manuscript_id,
                editorId=red.evaluator_id,
                editorName=red.evaluator.full_name,
                annotationType="redaction",
                pageNumber=red.page_number,
                xPosition=red.x_position,
                yPosition=red.y_position,
                positionData=red.position_data,
                comment=red.comment,
                contentData=red.content_data,
                createdAt=red.created_at,
                updatedAt=red.updated_at
            )
            for red in redactions
        ]

    async def update_redaction(
        self,
        redaction_id: str,
        editor_id: int,
        data: RedactionUpdate
    ) -> RedactionResponse:
        """Update a redaction. Only creator can update."""
        logger.info(f"Updating redaction {redaction_id}")

        query = (
            select(ManuscriptAnnotation)
            .where(
                ManuscriptAnnotation.id == redaction_id,
                ManuscriptAnnotation.annotation_type == "redaction"
            )
            .options(selectinload(ManuscriptAnnotation.evaluator))
        )
        result = await self.db.execute(query)
        redaction = result.scalar_one_or_none()

        if not redaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Redaction not found"
            )

        if redaction.evaluator_id != editor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own redactions"
            )

        # Update
        redaction.comment = data.comment
        redaction.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(redaction)

        return RedactionResponse(
            id=redaction.id,
            manuscriptId=redaction.manuscript_id,
            editorId=redaction.evaluator_id,
            editorName=redaction.evaluator.full_name,
            annotationType="redaction",
            pageNumber=redaction.page_number,
            xPosition=redaction.x_position,
            yPosition=redaction.y_position,
            positionData=redaction.position_data,
            comment=redaction.comment,
            contentData=redaction.content_data,
            createdAt=redaction.created_at,
            updatedAt=redaction.updated_at
        )

    async def delete_redaction(
        self,
        redaction_id: str,
        editor_id: int
    ) -> dict:
        """Delete a redaction. Only creator can delete."""
        logger.info(f"Deleting redaction {redaction_id}")

        query = select(ManuscriptAnnotation).where(
            ManuscriptAnnotation.id == redaction_id,
            ManuscriptAnnotation.annotation_type == "redaction"
        )
        result = await self.db.execute(query)
        redaction = result.scalar_one_or_none()

        if not redaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Redaction not found"
            )

        if redaction.evaluator_id != editor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own redactions"
            )

        await self.db.delete(redaction)
        await self.db.commit()

        logger.info(f"Redaction {redaction_id} deleted successfully")
        return {"message": "Redaction deleted successfully"}

    async def mark_as_anonymized(
        self,
        manuscript_id: int,
        editor_id: int,
        data: AnonymizationStatusRequest
    ) -> AnonymizationStatusResponse:
        """
        Mark manuscript as anonymized.
        This enables evaluator assignment.
        """
        logger.info(f"Marking manuscript {manuscript_id} as anonymized by editor {editor_id}")

        # Get manuscript
        query = select(Manuscript).where(Manuscript.id == manuscript_id)
        result = await self.db.execute(query)
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found"
            )

        # Count redactions
        redaction_count_query = select(ManuscriptAnnotation).where(
            ManuscriptAnnotation.manuscript_id == manuscript_id,
            ManuscriptAnnotation.annotation_type == "redaction"
        )
        redaction_result = await self.db.execute(redaction_count_query)
        redaction_count = len(redaction_result.scalars().all())

        # Update manuscript
        manuscript.is_anonymized = True
        manuscript.anonymized_at = datetime.utcnow()
        manuscript.anonymized_by_id = editor_id

        await self.db.commit()
        await self.db.refresh(manuscript)

        # Get editor name
        editor_query = select(User).where(User.id == editor_id)
        editor_result = await self.db.execute(editor_query)
        editor = editor_result.scalar_one()

        logger.info(f"Manuscript {manuscript_id} marked as anonymized with {redaction_count} redactions")

        return AnonymizationStatusResponse(
            manuscriptId=manuscript.id,
            isAnonymized=manuscript.is_anonymized,
            anonymizedAt=manuscript.anonymized_at,
            anonymizedByName=editor.full_name,
            redactionCount=redaction_count
        )

    async def unmark_as_anonymized(
        self,
        manuscript_id: int,
        editor_id: int
    ) -> AnonymizationStatusResponse:
        """
        Remove anonymization flag.
        Useful if editor needs to add more redactions.
        """
        logger.info(f"Unmarking manuscript {manuscript_id} as anonymized")

        query = select(Manuscript).where(Manuscript.id == manuscript_id)
        result = await self.db.execute(query)
        manuscript = result.scalar_one_or_none()

        if not manuscript:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manuscript not found"
            )

        # Count redactions
        redaction_count_query = select(ManuscriptAnnotation).where(
            ManuscriptAnnotation.manuscript_id == manuscript_id,
            ManuscriptAnnotation.annotation_type == "redaction"
        )
        redaction_result = await self.db.execute(redaction_count_query)
        redaction_count = len(redaction_result.scalars().all())

        # Update manuscript
        manuscript.is_anonymized = False
        manuscript.anonymized_at = None
        manuscript.anonymized_by_id = None

        await self.db.commit()
        await self.db.refresh(manuscript)

        # Get editor name
        editor_query = select(User).where(User.id == editor_id)
        editor_result = await self.db.execute(editor_query)
        editor = editor_result.scalar_one()

        logger.info(f"Manuscript {manuscript_id} unmarked as anonymized")

        return AnonymizationStatusResponse(
            manuscriptId=manuscript.id,
            isAnonymized=False,
            anonymizedAt=None,
            anonymizedByName=editor.full_name,
            redactionCount=redaction_count
        )
