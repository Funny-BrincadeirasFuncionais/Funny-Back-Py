from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.turma import Turma
from app.schemas.turma import TurmaCreate, TurmaResponse, TurmaUpdate
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario
from app.models.responsavel import Responsavel

router = APIRouter(prefix="/turmas", tags=["Turmas"])


@router.get("/", response_model=List[TurmaResponse])
def list_turmas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Listar todas as turmas"""
    turmas = db.query(Turma).all()
    return turmas


@router.get("/{turma_id}", response_model=TurmaResponse)
def get_turma(
    turma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Buscar turma por ID"""
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if not turma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada"
        )
    return turma


@router.post("/", response_model=TurmaResponse, status_code=status.HTTP_201_CREATED)
def create_turma(
    turma_data: TurmaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Criar nova turma"""
    # se vier um responsavel_id, validar que ele existe
    if turma_data.responsavel_id is not None:
        resp = db.query(Responsavel).filter(Responsavel.id == turma_data.responsavel_id).first()
        if not resp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Responsável não encontrado"
            )
    new_turma = Turma(**turma_data.dict())
    db.add(new_turma)
    db.commit()
    db.refresh(new_turma)
    return new_turma


@router.put("/{turma_id}", response_model=TurmaResponse)
def update_turma(
    turma_id: int,
    turma_data: TurmaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Atualizar turma"""
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if not turma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada"
        )

    update_data = turma_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(turma, field, value)

    db.commit()
    db.refresh(turma)
    return turma


@router.delete("/{turma_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_turma(
    turma_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Deletar turma"""
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    if not turma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turma não encontrada"
        )

    db.delete(turma)
    db.commit()
