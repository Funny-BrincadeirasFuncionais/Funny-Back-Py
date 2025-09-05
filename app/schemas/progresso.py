from pydantic import BaseModel
from typing import Optional
from .crianca import CriancaResponse
from .atividade import AtividadeResponse


class ProgressoBase(BaseModel):
    pontuacao: int
    observacoes: Optional[str] = None
    concluida: bool = False
    crianca_id: int
    atividade_id: int


class ProgressoCreate(ProgressoBase):
    pass


class ProgressoUpdate(BaseModel):
    pontuacao: Optional[int] = None
    observacoes: Optional[str] = None
    concluida: Optional[bool] = None


class ProgressoResponse(ProgressoBase):
    id: int
    crianca: Optional[CriancaResponse] = None
    atividade: Optional[AtividadeResponse] = None
    
    class Config:
        from_attributes = True


class ProgressoResumo(BaseModel):
    total: int
    concluidas: int
    media_pontuacao: float
