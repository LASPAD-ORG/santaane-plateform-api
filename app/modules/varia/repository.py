from sqlmodel import Session, select
from typing import List, Optional
from app.models.varia import Varia

class VariaRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, varia: Varia) -> Varia:
        """Crée un nouveau varia en base de données."""
        self.session.add(varia)
        self.session.commit()
        self.session.refresh(varia)
        return varia

    def get_by_id(self, varia_id: int) -> Optional[Varia]:
        """Récupère un varia par son ID."""
        return self.session.get(Varia, varia_id)

    def get_all(self) -> List[Varia]:
        """Récupère tous les varia."""
        statement = select(Varia)
        return self.session.exec(statement).all()

    def update(self, varia: Varia) -> Varia:
        """Met à jour un varia existant."""
        self.session.add(varia)
        self.session.commit()
        self.session.refresh(varia)
        return varia

    def delete(self, varia: Varia):
        """Supprime un varia."""
        self.session.delete(varia)
        self.session.commit()
