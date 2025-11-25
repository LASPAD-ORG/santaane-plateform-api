"""
API routes for manuscripts module.
All endpoints mapped according to API_PAYLOAD_EXAMPLES.json
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, status as http_status
from typing import Optional, List

from app.core.security import get_current_user
from app.models.user import User
from app.modules.manuscripts.schemas import (
    ManuscriptCreate,
    ManuscriptUpdate,
    ManuscriptResponse,
    PaginatedManuscriptResponse,
    ManuscriptVersionCreate,
    ManuscriptVersionResponse,
    TimelineEvent,
    DiscussionCreate,
    DiscussionReplyCreate,
    DiscussionResponse,
    ReviewCommentResponse,
    SubmitManuscriptResponse,
    DeleteManuscriptResponse
)
from app.modules.manuscripts.service import ManuscriptService
from app.modules.manuscripts.utils import get_manuscript_service

router = APIRouter(prefix="/manuscripts", tags=["Manuscripts"])


# ==================== Manuscript CRUD ====================

@router.get("/", response_model=PaginatedManuscriptResponse)
async def get_manuscripts(
    status: Optional[str] = Query(None, description="Filter by status: draft, submitted, under_review, etc."),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    GET /api/v1/manuscripts - Récupérer tous les manuscrits de l'utilisateur

    Query parameters:
    - status: Filter by manuscript status (optional)
    - page: Page number (default: 1)
    - limit: Items per page (default: 20)
    """
    skip = (page - 1) * limit
    return await service.get_manuscripts(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status
    )


@router.get("/{manuscript_id}", response_model=ManuscriptResponse)
async def get_manuscript_by_id(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    GET /api/v1/manuscripts/{id} - Récupérer un manuscrit spécifique
    """
    return await service.get_manuscript_by_id(manuscript_id, current_user.id)


@router.post("/", response_model=ManuscriptResponse, status_code=http_status.HTTP_201_CREATED)
async def create_manuscript(
    title: str = Form(..., description="Manuscript title"),
    abstract: str = Form(..., description="Manuscript abstract"),
    keywords: str = Form(..., description="Comma-separated keywords"),
    categoryId: int = Form(..., description="Category ID"),
    coverImage: Optional[UploadFile] = File(None, description="Cover image file"),
    manuscriptFile: Optional[UploadFile] = File(None, description="Manuscript PDF file"),
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    POST /api/v1/manuscripts - Créer un nouveau manuscrit

    Supports multipart/form-data with:
    - title: Manuscript title
    - abstract: Manuscript abstract
    - keywords: Comma-separated keywords
    - categoryId: Category ID
    - coverImage: Cover image file (optional)
    - manuscriptFile: Manuscript PDF file (optional)
    """
    manuscript_data = ManuscriptCreate(
        title=title,
        abstract=abstract,
        keywords=keywords,
        categoryId=categoryId
    )

    return await service.create_manuscript(
        manuscript_data=manuscript_data,
        user_id=current_user.id,
        cover_image=coverImage,
        manuscript_file=manuscriptFile
    )


@router.put("/{manuscript_id}", response_model=ManuscriptResponse)
async def update_manuscript(
    manuscript_id: int,
    manuscript_data: ManuscriptUpdate,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    PUT /api/v1/manuscripts/{id} - Mettre à jour un manuscrit existant

    Only draft manuscripts can be updated.
    """
    return await service.update_manuscript(
        manuscript_id=manuscript_id,
        manuscript_data=manuscript_data,
        user_id=current_user.id
    )


@router.delete("/{manuscript_id}", response_model=DeleteManuscriptResponse)
async def delete_manuscript(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    DELETE /api/v1/manuscripts/{id} - Supprimer un manuscrit (uniquement les brouillons)
    """
    return await service.delete_manuscript(manuscript_id, current_user.id)


@router.post("/{manuscript_id}/submit", response_model=SubmitManuscriptResponse)
async def submit_manuscript(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    POST /api/v1/manuscripts/{id}/submit - Soumettre un manuscrit pour évaluation
    """
    return await service.submit_manuscript(manuscript_id, current_user.id)


@router.post("/{manuscript_id}/archive", response_model=ManuscriptResponse)
async def archive_manuscript(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    POST /api/v1/manuscripts/{id}/archive - Archiver un manuscrit
    """
    return await service.archive_manuscript(manuscript_id, current_user.id)


@router.post("/{manuscript_id}/unarchive", response_model=ManuscriptResponse)
async def unarchive_manuscript(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    POST /api/v1/manuscripts/{id}/unarchive - Désarchiver un manuscrit
    """
    return await service.unarchive_manuscript(manuscript_id, current_user.id)


# ==================== Manuscript Versions ====================

@router.post("/{manuscript_id}/versions", response_model=ManuscriptVersionResponse, status_code=http_status.HTTP_201_CREATED)
async def upload_new_version(
    manuscript_id: int,
    changesSummary: str = Form(..., description="Summary of changes in this version"),
    title: str = Form(..., description="Manuscript title"),
    abstract: Optional[str] = Form(None, description="Manuscript abstract"),
    keywords: Optional[str] = Form(None, description="Comma-separated keywords"),
    manuscriptFile: UploadFile = File(..., description="Manuscript PDF file"),
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    POST /api/v1/manuscripts/{id}/versions - Télécharger une nouvelle version du manuscrit

    Supports multipart/form-data with:
    - changesSummary: Summary of changes
    - title: Manuscript title
    - abstract: Manuscript abstract (optional)
    - keywords: Comma-separated keywords (optional)
    - manuscriptFile: Manuscript PDF file
    """
    version_data = ManuscriptVersionCreate(
        title=title,
        abstract=abstract,
        keywords=keywords,
        changesSummary=changesSummary
    )

    return await service.upload_new_version(
        manuscript_id=manuscript_id,
        version_data=version_data,
        user_id=current_user.id,
        manuscript_file=manuscriptFile
    )


@router.get("/{manuscript_id}/versions", response_model=List[ManuscriptVersionResponse])
async def get_manuscript_versions(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    GET /api/v1/manuscripts/{id}/versions - Récupérer toutes les versions d'un manuscrit
    """
    return await service.get_manuscript_versions(manuscript_id, current_user.id)


# ==================== Timeline ====================

@router.get("/{manuscript_id}/timeline", response_model=List[TimelineEvent])
async def get_manuscript_timeline(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    GET /api/v1/manuscripts/{id}/timeline - Récupérer l'historique d'un manuscrit
    """
    return await service.get_manuscript_timeline(manuscript_id, current_user.id)


# ==================== Discussions ====================

@router.get("/{manuscript_id}/discussions", response_model=List[DiscussionResponse])
async def get_manuscript_discussions(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    GET /api/v1/manuscripts/{id}/discussions - Récupérer les discussions sur un manuscrit
    """
    return await service.get_manuscript_discussions(manuscript_id, current_user.id)


@router.post("/{manuscript_id}/discussions", response_model=DiscussionResponse, status_code=http_status.HTTP_201_CREATED)
async def create_discussion(
    manuscript_id: int,
    discussion_data: DiscussionCreate,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    POST /api/v1/manuscripts/{id}/discussions - Créer une nouvelle discussion sur un manuscrit
    """
    return await service.create_discussion(
        manuscript_id=manuscript_id,
        discussion_data=discussion_data,
        user_id=current_user.id
    )


@router.post("/discussions/{discussion_id}/replies", response_model=DiscussionResponse, status_code=http_status.HTTP_201_CREATED)
async def reply_to_discussion(
    discussion_id: int,
    reply_data: DiscussionReplyCreate,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    POST /api/v1/discussions/{discussionId}/replies - Répondre à une discussion

    Note: This endpoint is under /manuscripts but logically belongs to discussions.
    The path matches the API specification.
    """
    return await service.reply_to_discussion(
        discussion_id=discussion_id,
        reply_data=reply_data,
        user_id=current_user.id
    )


# ==================== Review Comments ====================

@router.get("/{manuscript_id}/comments", response_model=List[ReviewCommentResponse])
async def get_review_comments(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    GET /api/v1/manuscripts/{id}/comments - Récupérer les commentaires des évaluateurs
    """
    return await service.get_review_comments(manuscript_id, current_user.id)


# ==================== Categories Router ====================
# Separate router for categories

categories_router = APIRouter(prefix="/categories", tags=["Categories"])


@categories_router.get("/", response_model=List[dict])
async def get_categories(
    current_user: User = Depends(get_current_user),
    service: ManuscriptService = Depends(get_manuscript_service)
):
    """
    GET /api/v1/categories - Récupérer toutes les catégories disponibles

    Returns a list of all active categories.
    """
    categories = await service.repository.get_all_categories()

    return [
        {
            "id": category.id,
            "name": category.name,
            "description": category.description
        }
        for category in categories
    ]
