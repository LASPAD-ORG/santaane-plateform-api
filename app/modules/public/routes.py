"""
Public module - API routes
No authentication required - public access to published manuscripts
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List

from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.public.repository import PublicRepository
from app.modules.public.service import PublicService
from app.modules.public.schemas import (
    PublicManuscriptListResponse,
    PublicManuscriptDetail,
    PublicManuscriptSummary,
    PublicAuthorDetail
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/public", tags=["Public"])


async def get_public_service(db: AsyncSession = Depends(get_db)) -> PublicService:
    """Dependency to get public service"""
    repository = PublicRepository(db)
    return PublicService(repository)


@router.get(
    "/manuscripts",
    response_model=PublicManuscriptListResponse,
    summary="Rechercher les manuscrits publiés"
)
async def search_manuscripts(
    q: Optional[str] = Query(None, description="Recherche dans le titre, résumé, mots-clés"),
    themeId: Optional[int] = Query(None, description="Filtrer par thème"),
    sectionId: Optional[int] = Query(None, description="Filtrer par section"),
    languageId: Optional[int] = Query(None, description="Filtrer par langue"),
    authorId: Optional[int] = Query(None, description="Filtrer par auteur"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    pageSize: int = Query(20, ge=1, le=100, description="Nombre d'éléments par page"),
    service: PublicService = Depends(get_public_service)
):
    """
    Rechercher et filtrer les manuscrits publiés.
    
    Cette API est publique et ne nécessite pas d'authentification.
    
    - **q**: Recherche textuelle dans le titre, résumé et mots-clés
    - **themeId**: Filtrer par ID de thème
    - **sectionId**: Filtrer par ID de section
    - **languageId**: Filtrer par ID de langue
    - **authorId**: Filtrer par ID d'auteur
    - **page**: Numéro de page (commence à 1)
    - **pageSize**: Nombre d'éléments par page (max 100)
    """
    logger.info(f"Public search request: q={q}, page={page}")
    
    return await service.search_manuscripts(
        query=q,
        theme_id=themeId,
        section_id=sectionId,
        language_id=languageId,
        author_id=authorId,
        page=page,
        page_size=pageSize
    )


@router.get(
    "/manuscripts/recent",
    response_model=List[PublicManuscriptSummary],
    summary="Obtenir les publications récentes"
)
async def get_recent_publications(
    limit: int = Query(10, ge=1, le=50, description="Nombre de publications à retourner"),
    service: PublicService = Depends(get_public_service)
):
    """
    Obtenir les manuscrits publiés les plus récents.
    
    Idéal pour afficher sur la page d'accueil.
    """
    return await service.get_recent_publications(limit)


@router.get(
    "/manuscripts/{manuscript_id}",
    response_model=PublicManuscriptDetail,
    summary="Obtenir les détails d'un manuscrit"
)
async def get_manuscript_detail(
    manuscript_id: int,
    service: PublicService = Depends(get_public_service)
):
    """
    Obtenir les détails complets d'un manuscrit publié.
    
    Inclut les informations sur l'auteur.
    """
    manuscript = await service.get_manuscript_detail(manuscript_id)
    
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscrit non trouvé ou non publié"
        )
    
    return manuscript


@router.get(
    "/authors/{author_id}",
    response_model=PublicAuthorDetail,
    summary="Obtenir le profil public d'un auteur"
)
async def get_author_profile(
    author_id: int,
    service: PublicService = Depends(get_public_service)
):
    """
    Obtenir le profil public d'un auteur avec ses publications.
    """
    author = await service.get_author_profile(author_id)
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auteur non trouvé"
        )
    
    return author


@router.get(
    "/filters",
    summary="Obtenir les options de filtres"
)
async def get_filter_options(
    service: PublicService = Depends(get_public_service)
):
    """
    Obtenir les thèmes, sections et langues disponibles pour les filtres.
    """
    return await service.get_filters()


@router.get(
    "/stats",
    summary="Obtenir les statistiques publiques"
)
async def get_public_stats(
    service: PublicService = Depends(get_public_service)
):
    """
    Obtenir les statistiques publiques (nombre de publications, auteurs, etc.)
    """
    return await service.get_stats()
