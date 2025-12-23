"""
Manuscripts module - API routes
Handles HTTP endpoints for manuscript operations
"""
from fastapi import APIRouter, Depends, status
from typing import List
from app.modules.manuscripts.schemas import (
    ManuscriptSubmit, 
    ManuscriptResponse,
    ManuscriptListResponse,
    ManuscriptRevision,
    ManuscriptDetailResponse,
    ManuscriptUpdate,
    ManuscriptStatusUpdate,
    EvaluatorManuscriptResponse
)
from app.modules.manuscripts.service import ManuscriptService
from app.modules.manuscripts.utils import get_manuscript_service
from app.core.security import get_current_user
from app.core.permissions import require_role
from app.core.roles import UserRole
from app.models.user import User

router = APIRouter(prefix="/manuscripts", tags=["Manuscripts"])


@router.post(
    "/submit",
    response_model=ManuscriptResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.AUTHOR))]
)
async def submit_manuscript(
    manuscript_data: ManuscriptSubmit,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    Submit a new manuscript
    
    Requires AUTHOR role
    
    - **title**: Manuscript title (3-500 characters)
    - **abstract**: Manuscript abstract (min 10 characters)
    - **keywords**: Optional keywords
    - **themeId**: Optional theme ID
    - **sectionId**: Required section ID
    - **languageId**: Required language ID
    - **pdfFilename**: Name of the uploaded PDF file
    """
    return await service.submit_manuscript(manuscript_data, current_user.id)


@router.get(
    "/my-manuscripts",
    response_model=ManuscriptListResponse,
    dependencies=[Depends(require_role(UserRole.AUTHOR))]
)
async def get_my_manuscripts(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    Get all manuscripts submitted by the current author
    
    Requires AUTHOR role
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    return await service.get_my_manuscripts(
        author_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/all",
    response_model=ManuscriptListResponse,
    dependencies=[Depends(require_role(UserRole.EDITOR))]
)
async def get_all_manuscripts(
    theme_id: int | None = None,
    section_id: int | None = None,
    language_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    Get all manuscripts with optional filters
    
    Requires EDITOR role
    
    - **theme_id**: Optional filter by theme ID (can be null for manuscripts without theme)
    - **section_id**: Optional filter by section ID
    - **language_id**: Optional filter by language ID
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    return await service.get_all_manuscripts(
        theme_id=theme_id,
        section_id=section_id,
        language_id=language_id,
        skip=skip,
        limit=limit
    )


@router.get(
    "/detail/{manuscript_id}",
    response_model=ManuscriptDetailResponse,
    dependencies=[Depends(require_role(UserRole.EDITOR))]
)
async def get_manuscript_detail_for_staff(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    Get detailed manuscript information including author details
    
    Requires EDITOR role (also accessible by ADMIN and EVALUATOR)
    
    Returns complete manuscript information with author details:
    - Author email, full name, ORCID ID
    - Author bio, position, institution
    - Manuscript content and metadata
    
    - **manuscript_id**: ID of the manuscript to retrieve
    """
    return await service.get_manuscript_detail_for_staff(
        manuscript_id=manuscript_id
    )


@router.put(
    "/detail/{manuscript_id}",
    response_model=ManuscriptDetailResponse,
    dependencies=[Depends(require_role(UserRole.EDITOR))]
)
async def update_manuscript_by_staff(
    manuscript_id: int,
    update_data: ManuscriptUpdate,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    Update manuscript (all fields except status)
    
    Requires EDITOR role (also accessible by SUPER_ADMIN)
    
    Can update:
    - title, abstract, keywords
    - theme, section, language
    - PDF filename
    
    Cannot update status (use separate status endpoint)
    
    - **manuscript_id**: ID of the manuscript to update
    """
    return await service.update_manuscript_by_staff(
        manuscript_id=manuscript_id,
        update_data=update_data
    )


@router.put(
    "/detail/{manuscript_id}/status",
    response_model=ManuscriptDetailResponse,
    dependencies=[Depends(require_role(UserRole.EDITOR))]
)
async def update_manuscript_status(
    manuscript_id: int,
    status_data: ManuscriptStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    Update manuscript status only
    
    Requires EDITOR role (also accessible by SUPER_ADMIN)
    
    Allowed status values:
    - REVISION_REQUESTED: Request revisions from author
    - ACCEPTED: Accept the manuscript
    - REJECTED: Reject the manuscript
    - PUBLISHED: Mark as published
    
    When status is ACCEPTED or REJECTED, decision_at is automatically set.
    When status is PUBLISHED, published_at is automatically set.
    
    - **manuscript_id**: ID of the manuscript
    - **status**: New status value
    """
    return await service.update_manuscript_status(
        manuscript_id=manuscript_id,
        status_data=status_data
    )


@router.get(
    "/{manuscript_id}",
    response_model=ManuscriptResponse,
    dependencies=[Depends(require_role(UserRole.AUTHOR))]
)
async def get_manuscript_details(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    Get details of a specific manuscript
    
    Requires AUTHOR role
    
    Users can only view their own manuscripts
    
    - **manuscript_id**: ID of the manuscript to retrieve
    """
    return await service.get_manuscript_details(
        manuscript_id=manuscript_id,
        current_user_id=current_user.id
    )


@router.put(
    "/{manuscript_id}/revise",
    response_model=ManuscriptResponse,
    dependencies=[Depends(require_role(UserRole.AUTHOR))]
)
async def revise_manuscript(
    manuscript_id: int,
    revision_data: ManuscriptRevision,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    Revise a manuscript (only when status is REVISION_REQUESTED)
    
    Requires AUTHOR role
    
    After revision, the status will automatically change to RE_SUBMITTED
    
    - **manuscript_id**: ID of the manuscript to revise
    - **title**: Optional new title
    - **abstract**: Optional new abstract
    - **keywords**: Optional new keywords
    - **themeId**: Optional new theme ID
    - **sectionId**: Optional new section ID
    - **languageId**: Optional new language ID
    - **pdfFilename**: Optional new PDF filename (upload new file first)
    """
    return await service.revise_manuscript(
        manuscript_id=manuscript_id,
        revision_data=revision_data,
        current_user_id=current_user.id
    )


@router.get(
    "/my-assignments",
    response_model=List[EvaluatorManuscriptResponse],
    dependencies=[Depends(require_role(UserRole.EVALUATOR))],
    summary="Get my manuscript assignments (Evaluator)"
)
async def get_my_assignments(
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    Get all manuscripts assigned to the current evaluator.
    
    **Requires:** EVALUATOR role
    
    **Returns:**
    - List of manuscripts with assignment details
    - Does NOT include author information for privacy
    - Includes assignment status (PENDING, ACCEPTED, DECLINED)
    - Includes evaluation deadline if set
    """
    return await service.get_my_assignments(current_user.id)
