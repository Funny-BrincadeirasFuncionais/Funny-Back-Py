from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.progresso import Progresso
from app.schemas.progresso import ProgressoCreate, ProgressoResponse, ProgressoUpdate, ProgressoResumo
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(prefix="/progresso", tags=["Progresso"])


@router.post("/registrar", response_model=ProgressoResponse, status_code=status.HTTP_201_CREATED)
def registrar_progresso(
    progresso_data: ProgressoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registrar novo progresso"""
    new_progresso = Progresso(**progresso_data.dict())
    db.add(new_progresso)
    db.commit()
    db.refresh(new_progresso)
    return new_progresso


@router.get("/crianca/{crianca_id}", response_model=List[ProgressoResponse])
def get_progresso_crianca(
    crianca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Buscar progresso de uma criança específica"""
    progressos = db.query(Progresso).filter(Progresso.crianca_id == crianca_id).all()
    return progressos


@router.get("/atividade/{atividade_id}", response_model=List[ProgressoResponse])
def get_progresso_atividade(
    atividade_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Buscar progresso de uma atividade específica"""
    progressos = db.query(Progresso).filter(Progresso.atividade_id == atividade_id).all()
    return progressos


@router.get("/crianca/{crianca_id}/resumo", response_model=ProgressoResumo)
def get_resumo_progresso_crianca(
    crianca_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obter resumo do progresso de uma criança"""
    progressos = db.query(Progresso).filter(Progresso.crianca_id == crianca_id).all()
    
    if not progressos:
        return ProgressoResumo(total=0, concluidas=0, media_pontuacao=0.0)
    
    total = len(progressos)
    concluidas = sum(1 for p in progressos if p.concluida)
    media_pontuacao = sum(p.pontuacao for p in progressos) / total
    
    return ProgressoResumo(
        total=total,
        concluidas=concluidas,
        media_pontuacao=round(media_pontuacao, 2)
    )
