from pydantic import BaseModel, Field, field_validator
from typing import Optional
from .crianca import CriancaResponse
from .atividade import AtividadeResponse
from .usuario import UsuarioResponse


class ProgressoBase(BaseModel):
    pontuacao: int = Field(..., ge=0, le=10, description="Pontuação do mini-jogo (0 a 10)")
    observacoes: Optional[str] = None
    concluida: bool = True  # Se chegou no back, foi concluída
    crianca_id: int = Field(..., description="ID do aluno que realizou o mini-jogo")
    atividade_id: int = Field(..., description="ID da atividade (mini-jogo)")
    usuario_id: int = Field(..., description="ID do professor que aplicou a atividade")
    
    @field_validator('pontuacao')
    @classmethod
    def validate_pontuacao(cls, v):
        if v < 0 or v > 10:
            raise ValueError("Pontuação deve estar entre 0 e 10")
        return v


class ProgressoCreate(ProgressoBase):
    pass


class ProgressoUpdate(BaseModel):
    pontuacao: Optional[int] = Field(None, ge=0, le=10, description="Pontuação do mini-jogo (0 a 10)")
    observacoes: Optional[str] = None
    concluida: Optional[bool] = None
    
    @field_validator('pontuacao')
    @classmethod
    def validate_pontuacao(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError("Pontuação deve estar entre 0 e 10")
        return v


class ProgressoResponse(ProgressoBase):
    id: int
    crianca: Optional[CriancaResponse] = None
    atividade: Optional[AtividadeResponse] = None
    usuario: Optional[UsuarioResponse] = None
    
    class Config:
        from_attributes = True


class ProgressoResumo(BaseModel):
    total: int
    concluidas: int
    media_pontuacao: float
