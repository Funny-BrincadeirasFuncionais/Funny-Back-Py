from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.atividade import Atividade
from app.schemas.atividade import AtividadeCreate, AtividadeResponse, AtividadeUpdate
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/atividades", tags=["Atividades"])


@router.get("/", response_model=List[AtividadeResponse])
def list_atividades(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todas as atividades"""
    atividades = db.query(Atividade).all()
    return atividades


@router.get("/{atividade_id}", response_model=AtividadeResponse)
def get_atividade(
    atividade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Buscar atividade por ID"""
    atividade = db.query(Atividade).filter(Atividade.id == atividade_id).first()
    if not atividade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atividade não encontrada"
        )
    return atividade


@router.post("/", response_model=AtividadeResponse, status_code=status.HTTP_201_CREATED)
def create_atividade(
    atividade_data: AtividadeCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova atividade"""
    new_atividade = Atividade(**atividade_data.dict())
    db.add(new_atividade)
    db.commit()
    db.refresh(new_atividade)
    return new_atividade


@router.put("/{atividade_id}", response_model=AtividadeResponse)
def update_atividade(
    atividade_id: int,
    atividade_data: AtividadeUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar atividade"""
    atividade = db.query(Atividade).filter(Atividade.id == atividade_id).first()
    if not atividade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atividade não encontrada"
        )
    
    update_data = atividade_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(atividade, field, value)
    
    db.commit()
    db.refresh(atividade)
    return atividade


@router.delete("/{atividade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_atividade(
    atividade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Deletar atividade"""
    atividade = db.query(Atividade).filter(Atividade.id == atividade_id).first()
    if not atividade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atividade não encontrada"
        )
    
    db.delete(atividade)
    db.commit()
