from pydantic import BaseModel
from typing import Optional
from .responsavel import ResponsavelResponse


class TurmaBase(BaseModel):
    nome: str


class TurmaCreate(TurmaBase):
    responsavel_id: Optional[int] = None


class TurmaUpdate(BaseModel):
    nome: Optional[str] = None
    responsavel_id: Optional[int] = None


class TurmaResponse(TurmaBase):
    id: int
    responsavel_id: Optional[int] = None
    responsavel: Optional[ResponsavelResponse] = None
    
    class Config:
        from_attributes = True
