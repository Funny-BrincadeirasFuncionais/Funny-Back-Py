from pydantic import BaseModel, EmailStr
from typing import Optional


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    senha: str


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioResponse(UsuarioBase):
    id: int
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    responsavel_id: Optional[int] = None
