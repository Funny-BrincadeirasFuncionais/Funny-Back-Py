from pydantic import BaseModel, EmailStr
from typing import Optional, List


class ResponsavelBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: str


class ResponsavelCreate(ResponsavelBase):
    pass


class ResponsavelUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None


class ResponsavelResponse(ResponsavelBase):
    id: int
    # lista de IDs das turmas associadas (evita import circular com schemas.turma)
    turmas: Optional[List[int]] = None
    
    # Pydantic v2: allow parsing from ORM objects' attributes when needed
    model_config = {"from_attributes": True}
