from pydantic import BaseModel, EmailStr
from typing import Optional


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
    
    class Config:
        from_attributes = True
