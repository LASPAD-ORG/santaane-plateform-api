from sqlmodel import Session, Depends
from fastapi import Depends, HTTPException, status
from typing import List
from app.db import get_session
from app.models.varia import Varia
from app.modules.varia.repository import VariaRepository
from app.modules.varia.schemas import VariaCreate, VariaUpdate, VariaRead

class VariaService:
    def __init__(self, session: Session = Depends(get_session)):
        self.repository = VariaRepository(session)
    
    def create_varia(self, varia_data: VariaCreate) -> VariaRead:
        """Crée un nouveau varia."""

        varia = Varia.model_validate(varia_data)
        varia = self.repository.create(varia)
        return VariaRead.model_validate(varia)

    def get_all_varias(self) -> List[VariaRead]:
        """Récupère tous les varia actifs et inactifs."""
        varias = self.repository.get_all()
        return [VariaRead.model_validate(v) for v in varias]

    def get_varia_by_id(self, varia_id: int) -> VariaRead:
        """Récupère un varia spécifique."""
        varia = self.repository.get_by_id(varia_id)
        if not varia:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Varia non trouvé.")
        return VariaRead.model_validate(varia)

    def update_varia(self, varia_id: int, update_data: VariaUpdate) -> VariaRead:
        """Met à jour un varia existant."""
        varia = self.repository.get_by_id(varia_id)
        if not varia:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Varia non trouvé.")
        
        data_to_update = update_data.model_dump(exclude_unset=True)
        varia.model_validate(data_to_update)

        varia = self.repository.update(varia)
        return VariaRead.model_validate(varia)

    def delete_varia(self, varia_id: int):
        """Supprime un varia et vérifie qu'il n'est plus lié à des manuscrits."""
        varia = self.repository.get_by_id(varia_id)
        if not varia:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Varia non trouvé.")
            
        if varia.manuscripts:
             raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Impossible de supprimer : ce varia est lié à des manuscrits existants."
            )
            
        self.repository.delete(varia)
