from pydantic import BaseModel
from typing import Optional


class AtividadeBase(BaseModel):
    titulo: str
    descricao: str
    categoria: str
    nivel_dificuldade: int


class AtividadeCreate(AtividadeBase):
    pass


class AtividadeUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    nivel_dificuldade: Optional[int] = None


class AtividadeResponse(AtividadeBase):
    id: int
    
    class Config:
        from_attributes = True
