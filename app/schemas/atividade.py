from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


CATEGORIAS_MINIJOGOS = Literal["Matemáticas", "Português", "Lógica", "Cotidiano"]


class AtividadeBase(BaseModel):
    categoria: CATEGORIAS_MINIJOGOS = Field(..., description="Categoria do mini-jogo: Matemáticas, Português, Lógica ou Cotidiano")
    titulo: Optional[str] = Field(None, description="Título do mini-jogo (opcional - pode ser gerado no front)")
    descricao: Optional[str] = Field(None, description="Descrição do mini-jogo (opcional - pode ser gerado no front)")
    
    @field_validator('categoria')
    @classmethod
    def validate_categoria(cls, v):
        categorias_validas = ["Matemáticas", "Português", "Lógica", "Cotidiano"]
        if v not in categorias_validas:
            raise ValueError(f"Categoria deve ser uma das seguintes: {', '.join(categorias_validas)}")
        return v


class AtividadeCreate(BaseModel):
    """Schema para criar atividade - só precisa da categoria (o front roda tudo)"""
    categoria: CATEGORIAS_MINIJOGOS = Field(..., description="Categoria do mini-jogo: Matemáticas, Português, Lógica ou Cotidiano")
    titulo: Optional[str] = Field(None, description="Título do mini-jogo (opcional)")
    descricao: Optional[str] = Field(None, description="Descrição do mini-jogo (opcional)")
    
    @field_validator('categoria')
    @classmethod
    def validate_categoria(cls, v):
        categorias_validas = ["Matemáticas", "Português", "Lógica", "Cotidiano"]
        if v not in categorias_validas:
            raise ValueError(f"Categoria deve ser uma das seguintes: {', '.join(categorias_validas)}")
        return v


class AtividadeUpdate(BaseModel):
    categoria: Optional[CATEGORIAS_MINIJOGOS] = Field(None, description="Categoria do mini-jogo")
    titulo: Optional[str] = Field(None, description="Título do mini-jogo")
    descricao: Optional[str] = Field(None, description="Descrição do mini-jogo")
    
    @field_validator('categoria')
    @classmethod
    def validate_categoria(cls, v):
        if v is not None:
            categorias_validas = ["Matemáticas", "Português", "Lógica", "Cotidiano"]
            if v not in categorias_validas:
                raise ValueError(f"Categoria deve ser uma das seguintes: {', '.join(categorias_validas)}")
        return v


class AtividadeResponse(AtividadeBase):
    id: int
    
    class Config:
        from_attributes = True
