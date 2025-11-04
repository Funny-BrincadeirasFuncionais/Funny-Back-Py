from pydantic import BaseModel, Field, field_validator
from typing import Optional
from .crianca import CriancaResponse
from .atividade import AtividadeResponse
from .usuario import UsuarioResponse


class ProgressoBase(BaseModel):
    pontuacao: int = Field(..., ge=0, description="Pontuação do mini-jogo")
    observacoes: Optional[str] = None
    concluida: bool = True  # Se chegou no back, foi concluída
    crianca_id: int = Field(..., description="ID do aluno que realizou o mini-jogo")
    atividade_id: int = Field(..., description="ID da atividade (mini-jogo)")
    usuario_id: Optional[int] = Field(None, description="ID do professor que aplicou a atividade (opcional, preenchido automaticamente)")
    
    @field_validator('pontuacao')
    @classmethod
    def validate_pontuacao(cls, v):
        if v < 0:
            raise ValueError("Pontuação deve ser maior ou igual a 0")
        return v


class ProgressoCreate(BaseModel):
    """Schema para criar progresso - front-end envia apenas crianca_id, atividade_id, pontuacao, observacoes e concluida"""
    pontuacao: int = Field(..., ge=0, description="Pontuação do mini-jogo")
    observacoes: Optional[str] = None
    concluida: bool = Field(default=True, description="Se a atividade foi concluída")
    crianca_id: int = Field(..., description="ID do aluno que realizou o mini-jogo")
    atividade_id: int = Field(..., description="ID da atividade (mini-jogo)")
    usuario_id: Optional[int] = Field(None, description="ID do professor (opcional, preenchido automaticamente do token)")
    
    @field_validator('pontuacao')
    @classmethod
    def validate_pontuacao(cls, v):
        if v < 0:
            raise ValueError("Pontuação deve ser maior ou igual a 0")
        return v


class ProgressoUpdate(BaseModel):
    pontuacao: Optional[int] = Field(None, ge=0, description="Pontuação do mini-jogo")
    observacoes: Optional[str] = None
    concluida: Optional[bool] = None
    
    @field_validator('pontuacao')
    @classmethod
    def validate_pontuacao(cls, v):
        if v is not None and v < 0:
            raise ValueError("Pontuação deve ser maior ou igual a 0")
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
