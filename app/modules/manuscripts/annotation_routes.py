"""
API routes for manuscript annotations
"""
from fastapi import APIRouter, Depends, status
from typing import List
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import require_role, get_current_user
from app.core.roles import UserRole
from app.models.user import User
from app.modules.manuscripts.annotation_schemas import (
    AnnotationCreate,
    AnnotationUpdate,
    AnnotationResponse
)
from app.modules.manuscripts.annotation_service import AnnotationService


router = APIRouter(prefix="/manuscripts", tags=["Manuscript Annotations"])


@router.post(
    "/{manuscript_id}/annotations",
    response_model=AnnotationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.EVALUATOR))],
    summary="Create annotation on manuscript"
)
async def create_annotation(
    manuscript_id: int,
    data: AnnotationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new annotation on a manuscript PDF.
    
    **Requires:** EVALUATOR role + ACCEPTED assignment
    
    **Parameters:**
    - **manuscript_id**: ID of the manuscript
    - **pageNumber**: Page number in the PDF (1-based)
    - **xPosition**: X coordinate on the page
    - **yPosition**: Y coordinate on the page
    - **comment**: The annotation comment
    - **highlightedText**: Optional text that was highlighted
    
    **Returns:** Created annotation with details
    """
    service = AnnotationService(db)
    return await service.create_annotation(
        manuscript_id=manuscript_id,
        evaluator_id=current_user.id,
        data=data
    )


@router.get(
    "/{manuscript_id}/annotations",
    response_model=List[AnnotationResponse],
    dependencies=[Depends(require_role(UserRole.EVALUATOR))],
    summary="Get my annotations for manuscript"
)
async def get_my_annotations(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all your annotations for a specific manuscript.
    
    **Requires:** EVALUATOR role + assignment to manuscript
    
    **Returns:** List of annotations ordered by page number and creation time
    """
    service = AnnotationService(db)
    return await service.get_manuscript_annotations(
        manuscript_id=manuscript_id,
        evaluator_id=current_user.id
    )


@router.put(
    "/annotations/{annotation_id}",
    response_model=AnnotationResponse,
    dependencies=[Depends(require_role(UserRole.EVALUATOR))],
    summary="Update annotation"
)
async def update_annotation(
    annotation_id: int,
    data: AnnotationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing annotation.
    
    **Requires:** EVALUATOR role + must be the annotation creator
    
    **Parameters:**
    - **annotation_id**: ID of the annotation to update
    - **comment**: Updated comment text
    
    **Returns:** Updated annotation
    """
    service = AnnotationService(db)
    return await service.update_annotation(
        annotation_id=annotation_id,
        evaluator_id=current_user.id,
        data=data
    )


@router.delete(
    "/annotations/{annotation_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.EVALUATOR))],
    summary="Delete annotation"
)
async def delete_annotation(
    annotation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an annotation.
    
    **Requires:** EVALUATOR role + must be the annotation creator
    
    **Parameters:**
    - **annotation_id**: ID of the annotation to delete
    
    **Returns:** Success message
    """
    service = AnnotationService(db)
    return await service.delete_annotation(
        annotation_id=annotation_id,
        evaluator_id=current_user.id
    )
