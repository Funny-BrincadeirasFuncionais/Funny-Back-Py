from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.diagnostico import Diagnostico
from app.schemas.diagnostico import DiagnosticoCreate, DiagnosticoResponse, DiagnosticoUpdate
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/diagnosticos", tags=["Diagnósticos"])


@router.get("/", response_model=List[DiagnosticoResponse])
def list_diagnosticos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todos os diagnósticos"""
    diagnosticos = db.query(Diagnostico).all()
    return diagnosticos


@router.get("/{diagnostico_id}", response_model=DiagnosticoResponse)
def get_diagnostico(
    diagnostico_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Buscar diagnóstico por ID"""
    diagnostico = db.query(Diagnostico).filter(Diagnostico.id == diagnostico_id).first()
    if not diagnostico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico não encontrado"
        )
    return diagnostico


@router.post("/", response_model=DiagnosticoResponse, status_code=status.HTTP_201_CREATED)
def create_diagnostico(
    diagnostico_data: DiagnosticoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo diagnóstico"""
    new_diagnostico = Diagnostico(**diagnostico_data.dict())
    db.add(new_diagnostico)
    db.commit()
    db.refresh(new_diagnostico)
    return new_diagnostico


@router.put("/{diagnostico_id}", response_model=DiagnosticoResponse)
def update_diagnostico(
    diagnostico_id: int,
    diagnostico_data: DiagnosticoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar diagnóstico"""
    diagnostico = db.query(Diagnostico).filter(Diagnostico.id == diagnostico_id).first()
    if not diagnostico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico não encontrado"
        )
    
    update_data = diagnostico_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(diagnostico, field, value)
    
    db.commit()
    db.refresh(diagnostico)
    return diagnostico


@router.delete("/{diagnostico_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diagnostico(
    diagnostico_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Deletar diagnóstico"""
    diagnostico = db.query(Diagnostico).filter(Diagnostico.id == diagnostico_id).first()
    if not diagnostico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnóstico não encontrado"
        )
    
    db.delete(diagnostico)
    db.commit()
