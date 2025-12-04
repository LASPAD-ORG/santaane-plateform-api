from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.modules.varia.schemas import VariaCreate, VariaUpdate, VariaRead
from app.modules.varia.service import VariaService
from app.core.security import get_current_active_user
from app.core.permissions import RoleChecker

ADMIN_ROLES = ["SUPER_ADMIN", "EDITOR"] 
VARIA_MANAGER_REQUIRED = RoleChecker(ADMIN_ROLES)

router = APIRouter(
    prefix="/varias",
    tags=["Varia/Thématiques"],
    dependencies=[Depends(get_current_active_user), Depends(VARIA_MANAGER_REQUIRED)]
)


@router.post(
    "/",
    response_model=VariaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau Varia/Thématique"
)
def create_varia(
    varia_data: VariaCreate,
    varia_service: VariaService = Depends(VariaService)
):
    """Crée une nouvelle catégorie ou thématique pour l'organisation des manuscrits."""
    return varia_service.create_varia(varia_data)


@router.get(
    "/",
    response_model=List[VariaRead],
    summary="Lister tous les Varia/Thématiques"
)
def list_varias(varia_service: VariaService = Depends(VariaService)):
    """Récupère la liste de tous les varia existants."""
    return varia_service.get_all_varias()


@router.get(
    "/{varia_id}",
    response_model=VariaRead,
    summary="Obtenir un Varia spécifique"
)
def get_varia(
    varia_id: int,
    varia_service: VariaService = Depends(VariaService)
):
    """Récupère un varia par son ID."""
    return varia_service.get_varia_by_id(varia_id)


@router.patch(
    "/{varia_id}",
    response_model=VariaRead,
    summary="Mettre à jour un Varia"
)
def update_varia(
    varia_id: int,
    update_data: VariaUpdate,
    varia_service: VariaService = Depends(VariaService)
):
    """Met à jour le nom, la description ou le statut actif d'un varia."""
    return varia_service.update_varia(varia_id, update_data)


@router.delete(
    "/{varia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un Varia (uniquement si non utilisé)"
)
def delete_varia(
    varia_id: int,
    varia_service: VariaService = Depends(VariaService)
):
    """Supprime un varia. Requiert qu'aucun manuscrit n'y soit attaché."""
    varia_service.delete_varia(varia_id)
