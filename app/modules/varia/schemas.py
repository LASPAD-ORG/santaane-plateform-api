from typing import Optional, List
from pydantic import BaseModel, Field

# Base
class VariaBase(BaseModel):
    name: str = Field(..., max_length=150, description="Nom du varia ou de la thématique.")
    description: Optional[str] = Field(default=None, description="Description détaillée du varia.")
    is_active: bool = Field(default=True, description="Indique si le varia accepte de nouvelles soumissions.")

# Entrée API
class VariaCreate(VariaBase):
    pass

class VariaUpdate(VariaBase):
    name: Optional[str] = None
    
class VariaRead(VariaBase):
    id: int
    

    
    class Config:
        from_attributes = True

class VariaListRead(VariaRead):
    pass
