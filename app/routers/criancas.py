from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.crianca import Crianca
from app.schemas.crianca import CriancaCreate, CriancaResponse, CriancaUpdate
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/criancas", tags=["Crianças"])


@router.get("/", response_model=List[CriancaResponse])
def list_criancas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todas as crianças"""
    criancas = db.query(Crianca).all()
    return criancas


@router.get("/{crianca_id}", response_model=CriancaResponse)
def get_crianca(
    crianca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Buscar criança por ID"""
    crianca = db.query(Crianca).filter(Crianca.id == crianca_id).first()
    if not crianca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Criança não encontrada"
        )
    return crianca


@router.post("/", response_model=CriancaResponse, status_code=status.HTTP_201_CREATED)
def create_crianca(
    crianca_data: CriancaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova criança"""
    new_crianca = Crianca(**crianca_data.dict())
    db.add(new_crianca)
    db.commit()
    db.refresh(new_crianca)
    return new_crianca


@router.put("/{crianca_id}", response_model=CriancaResponse)
def update_crianca(
    crianca_id: int,
    crianca_data: CriancaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar criança"""
    crianca = db.query(Crianca).filter(Crianca.id == crianca_id).first()
    if not crianca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Criança não encontrada"
        )
    
    update_data = crianca_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(crianca, field, value)
    
    db.commit()
    db.refresh(crianca)
    return crianca


@router.delete("/{crianca_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_crianca(
    crianca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Deletar criança"""
    crianca = db.query(Crianca).filter(Crianca.id == crianca_id).first()
    if not crianca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Criança não encontrada"
        )
    
    db.delete(crianca)
    db.commit()
