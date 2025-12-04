from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.abstract_model import AbstractModel
# Un Varia peut être ACTIF ou INACTIF, par exemple (ou utiliser un enum simple si nécessaire)
# from app.models.enums import VariaStatus 

if TYPE_CHECKING:
    from app.models.manuscript import Manuscript


class Varia(AbstractModel, table=True):
    __tablename__ = "varias"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False, max_length=150)
    description: Optional[str] = Field(default=None)
    
    is_active: bool = Field(default=True, nullable=False)
    manuscripts: List["Manuscript"] = Relationship(back_populates="varia")
