"""
Manuscripts module - API routes
Handles HTTP endpoints for manuscript operations
"""
from fastapi import APIRouter, Depends, status
from app.modules.manuscripts.schemas import (
    ManuscriptSubmit, 
    ManuscriptResponse,
    ManuscriptListResponse
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
