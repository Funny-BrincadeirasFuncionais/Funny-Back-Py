from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.responsavel import Responsavel
from app.schemas.responsavel import ResponsavelCreate, ResponsavelResponse, ResponsavelUpdate
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/responsaveis", tags=["Responsáveis"])


@router.get("/", response_model=List[ResponsavelResponse])
def list_responsaveis(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todos os responsáveis"""
    responsaveis = db.query(Responsavel).all()
    return responsaveis


@router.get("/{responsavel_id}", response_model=ResponsavelResponse)
def get_responsavel(
    responsavel_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Buscar responsável por ID"""
    responsavel = db.query(Responsavel).filter(Responsavel.id == responsavel_id).first()
    if not responsavel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Responsável não encontrado"
        )
    return responsavel


@router.post("/", response_model=ResponsavelResponse, status_code=status.HTTP_201_CREATED)
def create_responsavel(
    responsavel_data: ResponsavelCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar novo responsável"""
    new_responsavel = Responsavel(**responsavel_data.dict())
    db.add(new_responsavel)
    db.commit()
    db.refresh(new_responsavel)
    return new_responsavel


@router.put("/{responsavel_id}", response_model=ResponsavelResponse)
def update_responsavel(
    responsavel_id: int,
    responsavel_data: ResponsavelUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar responsável"""
    responsavel = db.query(Responsavel).filter(Responsavel.id == responsavel_id).first()
    if not responsavel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Responsável não encontrado"
        )
    
    update_data = responsavel_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(responsavel, field, value)
    
    db.commit()
    db.refresh(responsavel)
    return responsavel


@router.delete("/{responsavel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_responsavel(
    responsavel_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Deletar responsável"""
    responsavel = db.query(Responsavel).filter(Responsavel.id == responsavel_id).first()
    if not responsavel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Responsável não encontrado"
        )
    
    db.delete(responsavel)
    db.commit()
