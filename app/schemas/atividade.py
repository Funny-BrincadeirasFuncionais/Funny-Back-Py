from pydantic import BaseModel, Field, field_validator
from typing import Optional


class AtividadeBase(BaseModel):
    categoria: str = Field(..., description="Categoria do mini-jogo: Matemática(s), Português, Lógica ou Cotidiano")
    titulo: str = Field(..., description="Título do mini-jogo")
    descricao: str = Field(..., description="Descrição do mini-jogo")
    nivel_dificuldade: int = Field(default=1, description="Nível de dificuldade (padrão: 1)")
    
    @field_validator('categoria')
    @classmethod
    def validate_categoria(cls, v):
        # Normalizar categoria (aceitar tanto "Matemática" quanto "Matemáticas")
        v_normalizado = v.strip()
        # Mapear variações para formato padrão
        if v_normalizado.lower() in ["matemática", "matemáticas"]:
            return "Matemáticas"
        if v_normalizado.lower() == "português":
            return "Português"
        if v_normalizado.lower() == "lógica":
            return "Lógica"
        if v_normalizado.lower() == "cotidiano":
            return "Cotidiano"
        # Se já estiver no formato correto, retornar como está
        categorias_validas = ["Matemáticas", "Português", "Lógica", "Cotidiano"]
        if v_normalizado in categorias_validas:
            return v_normalizado
        raise ValueError(f"Categoria deve ser uma das seguintes: Matemática(s), Português, Lógica ou Cotidiano")


class AtividadeCreate(BaseModel):
    """Schema para criar atividade - front-end envia titulo, descricao, categoria e nivel_dificuldade"""
    titulo: str = Field(..., description="Título do mini-jogo")
    descricao: str = Field(..., description="Descrição do mini-jogo")
    categoria: str = Field(..., description="Categoria do mini-jogo: Matemática(s), Português, Lógica ou Cotidiano")
    nivel_dificuldade: int = Field(default=1, description="Nível de dificuldade (padrão: 1)")
    
    @field_validator('categoria')
    @classmethod
    def validate_categoria(cls, v):
        # Normalizar categoria (aceitar tanto "Matemática" quanto "Matemáticas")
        v_normalizado = v.strip()
        # Mapear variações para formato padrão
        if v_normalizado.lower() in ["matemática", "matemáticas"]:
            return "Matemáticas"
        if v_normalizado.lower() == "português":
            return "Português"
        if v_normalizado.lower() == "lógica":
            return "Lógica"
        if v_normalizado.lower() == "cotidiano":
            return "Cotidiano"
        # Se já estiver no formato correto, retornar como está
        categorias_validas = ["Matemáticas", "Português", "Lógica", "Cotidiano"]
        if v_normalizado in categorias_validas:
            return v_normalizado
        raise ValueError(f"Categoria deve ser uma das seguintes: Matemática(s), Português, Lógica ou Cotidiano")


class AtividadeUpdate(BaseModel):
    categoria: Optional[str] = Field(None, description="Categoria do mini-jogo")
    titulo: Optional[str] = Field(None, description="Título do mini-jogo")
    descricao: Optional[str] = Field(None, description="Descrição do mini-jogo")
    nivel_dificuldade: Optional[int] = Field(None, description="Nível de dificuldade")
    
    @field_validator('categoria')
    @classmethod
    def validate_categoria(cls, v):
        if v is not None:
            # Normalizar categoria (aceitar tanto "Matemática" quanto "Matemáticas")
            v_normalizado = v.strip()
            if v_normalizado.lower() in ["matemática", "matemáticas"]:
                return "Matemáticas"
            if v_normalizado.lower() == "português":
                return "Português"
            if v_normalizado.lower() == "lógica":
                return "Lógica"
            if v_normalizado.lower() == "cotidiano":
                return "Cotidiano"
            categorias_validas = ["Matemáticas", "Português", "Lógica", "Cotidiano"]
            if v_normalizado in categorias_validas:
                return v_normalizado
            raise ValueError(f"Categoria deve ser uma das seguintes: Matemática(s), Português, Lógica ou Cotidiano")
        return v


class AtividadeResponse(AtividadeBase):
    id: int
    
    class Config:
        from_attributes = True
