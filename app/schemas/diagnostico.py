from pydantic import BaseModel
from typing import Optional


class DiagnosticoBase(BaseModel):
    tipo: str


class DiagnosticoCreate(DiagnosticoBase):
    pass


class DiagnosticoUpdate(BaseModel):
    tipo: Optional[str] = None


class DiagnosticoResponse(DiagnosticoBase):
    id: int
    
    class Config:
        from_attributes = True
