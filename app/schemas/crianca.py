from pydantic import BaseModel
from typing import Optional
from .turma import TurmaResponse  # noqa: F401 (mantido se usado em outros lugares)
from .diagnostico import DiagnosticoResponse  # noqa: F401


class CriancaBase(BaseModel):
    nome: str
    idade: int
    # A criança pertence a uma turma e pode ter um diagnóstico associado
    turma_id: Optional[int] = None
    diagnostico_id: Optional[int] = None


class CriancaCreate(CriancaBase):
    """Campos aceitos para criação de criança.
    - Permite criar sem turma e/ou diagnóstico e atribuir depois via PUT.
    """
    pass


class CriancaUpdate(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None
    turma_id: Optional[int] = None
    diagnostico_id: Optional[int] = None


class CriancaResponse(BaseModel):
    id: int
    nome: str
    idade: int
    turma_id: Optional[int] = None
    diagnostico_id: Optional[int] = None
    # Simplificado para evitar erros de serialização por relacionamentos profundos
    # (se precisar dos objetos aninhados, montar manualmente no router como em turmas)

    class Config:
        from_attributes = True
