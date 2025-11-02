from pydantic import BaseModel
from typing import Optional
from .turma import TurmaResponse
from .diagnostico import DiagnosticoResponse


class CriancaBase(BaseModel):
    nome: str
    idade: int
    responsavel_id: int
    diagnostico_id: int


class CriancaCreate(CriancaBase):
    pass


class CriancaUpdate(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None
    turma_id: Optional[int] = None
    diagnostico_id: Optional[int] = None


class CriancaResponse(CriancaBase):
    id: int
    turma: Optional[TurmaResponse] = None
    diagnostico: Optional[DiagnosticoResponse] = None
    
    class Config:
        from_attributes = True
