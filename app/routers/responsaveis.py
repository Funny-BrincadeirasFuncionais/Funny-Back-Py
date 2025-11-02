from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.responsavel import Responsavel
from app.schemas.responsavel import ResponsavelCreate, ResponsavelResponse, ResponsavelUpdate
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario
from typing import List as _List

router = APIRouter(prefix="/responsaveis", tags=["Responsáveis"])


@router.get("/", response_model=List[ResponsavelResponse])
def list_responsaveis(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todos os responsáveis"""
    responsaveis = db.query(Responsavel).all()
    # converter para lista de dicts incluindo apenas os campos esperados pelo schema
    result = []
    for r in responsaveis:
        turma_ids = [t.id for t in getattr(r, "turmas", [])]
        result.append({
            "id": r.id,
            "nome": r.nome,
            "email": r.email,
            "telefone": r.telefone,
            "turmas": turma_ids,
        })
    return result


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
    turma_ids = [t.id for t in getattr(responsavel, "turmas", [])]
    return {
        "id": responsavel.id,
        "nome": responsavel.nome,
        "email": responsavel.email,
        "telefone": responsavel.telefone,
        "turmas": turma_ids,
    }


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
    return {
        "id": new_responsavel.id,
        "nome": new_responsavel.nome,
        "email": new_responsavel.email,
        "telefone": new_responsavel.telefone,
        "turmas": [],
    }


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
    turma_ids = [t.id for t in getattr(responsavel, "turmas", [])]
    return {
        "id": responsavel.id,
        "nome": responsavel.nome,
        "email": responsavel.email,
        "telefone": responsavel.telefone,
        "turmas": turma_ids,
    }


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
