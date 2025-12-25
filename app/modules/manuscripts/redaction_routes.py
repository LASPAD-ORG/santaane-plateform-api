"""
API routes for manuscript redactions (anonymization)
"""
from fastapi import APIRouter, Depends, status
from typing import List
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.permissions import require_role
from app.core.roles import UserRole
from app.models.user import User
from app.core.security import get_current_user
from app.modules.manuscripts.redaction_schemas import (
    RedactionCreate,
    RedactionUpdate,
    RedactionResponse,
    AnonymizationStatusRequest,
    AnonymizationStatusResponse
)
from app.modules.manuscripts.redaction_service import RedactionService


router = APIRouter(prefix="/manuscripts", tags=["Manuscript Redactions"])


@router.post(
    "/{manuscript_id}/redactions",
    response_model=RedactionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.EDITOR))],
    summary="Create redaction on manuscript (EDITOR only)"
)
async def create_redaction(
    manuscript_id: int,
    data: RedactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new redaction zone on a manuscript for anonymization.

    **Requires:** EDITOR role

    **Parameters:**
    - **manuscript_id**: ID of the manuscript
    - **pageNumber**: Page number in the PDF (1-based)
    - **xPosition**: X coordinate on the page
    - **yPosition**: Y coordinate on the page
    - **positionData**: JSON stringified position data
    - **comment**: Description of the redaction (default: "Zone anonymisée")
    - **contentData**: Optional JSON stringified content data

    **Returns:** Created redaction with UUID and details
    """
    service = RedactionService(db)
    return await service.create_redaction(
        manuscript_id=manuscript_id,
        editor_id=current_user.id,
        data=data
    )


@router.get(
    "/{manuscript_id}/redactions",
    response_model=List[RedactionResponse],
    dependencies=[Depends(require_role(UserRole.EDITOR))],
    summary="Get all redactions for manuscript (EDITOR only)"
)
async def get_manuscript_redactions(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all redaction zones for a specific manuscript.

    **Requires:** EDITOR role

    **Returns:** List of redactions ordered by page number
    """
    service = RedactionService(db)
    return await service.get_manuscript_redactions(
        manuscript_id=manuscript_id,
        editor_id=current_user.id
    )


@router.put(
    "/redactions/{redaction_id}",
    response_model=RedactionResponse,
    dependencies=[Depends(require_role(UserRole.EDITOR))],
    summary="Update redaction (EDITOR only)"
)
async def update_redaction(
    redaction_id: str,
    data: RedactionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing redaction.

    **Requires:** EDITOR role + must be the redaction creator

    **Parameters:**
    - **redaction_id**: UUID of the redaction to update
    - **comment**: Updated comment text

    **Returns:** Updated redaction
    """
    service = RedactionService(db)
    return await service.update_redaction(
        redaction_id=redaction_id,
        editor_id=current_user.id,
        data=data
    )


@router.delete(
    "/redactions/{redaction_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(UserRole.EDITOR))],
    summary="Delete redaction (EDITOR only)"
)
async def delete_redaction(
    redaction_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a redaction.

    **Requires:** EDITOR role + must be the redaction creator

    **Parameters:**
    - **redaction_id**: UUID of the redaction to delete

    **Returns:** Success message
    """
    service = RedactionService(db)
    return await service.delete_redaction(
        redaction_id=redaction_id,
        editor_id=current_user.id
    )


@router.post(
    "/{manuscript_id}/mark-anonymized",
    response_model=AnonymizationStatusResponse,
    dependencies=[Depends(require_role(UserRole.EDITOR))],
    summary="Mark manuscript as anonymized (EDITOR only)"
)
async def mark_manuscript_as_anonymized(
    manuscript_id: int,
    data: AnonymizationStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a manuscript as anonymized.
    This sets is_anonymized=true and enables evaluator assignment.

    **Requires:** EDITOR role

    **Parameters:**
    - **manuscript_id**: ID of the manuscript
    - **confirmAnonymized**: Confirmation flag (default: true)

    **Returns:** Anonymization status with timestamp and redaction count
    """
    service = RedactionService(db)
    return await service.mark_as_anonymized(
        manuscript_id=manuscript_id,
        editor_id=current_user.id,
        data=data
    )


@router.delete(
    "/{manuscript_id}/mark-anonymized",
    response_model=AnonymizationStatusResponse,
    dependencies=[Depends(require_role(UserRole.EDITOR))],
    summary="Unmark manuscript as anonymized (EDITOR only)"
)
async def unmark_manuscript_as_anonymized(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove anonymization flag from manuscript.
    Useful if editor needs to add more redactions.

    **Requires:** EDITOR role

    **Parameters:**
    - **manuscript_id**: ID of the manuscript

    **Returns:** Anonymization status
    """
    service = RedactionService(db)
    return await service.unmark_as_anonymized(
        manuscript_id=manuscript_id,
        editor_id=current_user.id
    )
