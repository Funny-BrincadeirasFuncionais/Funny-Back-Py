from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.progresso import Progresso
from app.models.atividade import Atividade
from app.schemas.progresso import ProgressoCreate, ProgressoResponse, ProgressoUpdate, ProgressoResumo
from app.schemas.atividade import AtividadeCreate
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/progresso", tags=["Progresso"])


class RegistrarMiniJogoRequest(BaseModel):
    """Request para registrar um mini-jogo completo
    O front roda o mini-jogo e envia apenas: nota, categoria e aluno
    """
    pontuacao: int = Field(..., ge=0, le=10, description="Pontuação obtida no mini-jogo (0 a 10)")
    categoria: str = Field(..., description="Categoria do mini-jogo: Matemáticas, Português, Lógica ou Cotidiano")
    crianca_id: int = Field(..., description="ID do aluno que realizou o mini-jogo")
    observacoes: Optional[str] = Field(None, description="Observações opcionais sobre o desempenho")


@router.post("/registrar-minijogo", response_model=ProgressoResponse, status_code=status.HTTP_201_CREATED)
def registrar_minijogo(
    request: RegistrarMiniJogoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registrar resultado de um mini-jogo completo
    
    Este endpoint é usado quando o front-end termina de rodar um mini-jogo.
    Cria automaticamente a atividade (com ID único) e registra o progresso.
    
    - **pontuacao**: Nota obtida (0 a 10)
    - **categoria**: Matemáticas, Português, Lógica ou Cotidiano
    - **crianca_id**: ID do aluno que realizou
    - **usuario_id**: Automático (professor logado)
    """
    # Validar categoria
    categorias_validas = ["Matemáticas", "Português", "Lógica", "Cotidiano"]
    if request.categoria not in categorias_validas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Categoria deve ser uma das seguintes: {', '.join(categorias_validas)}"
        )
    
    # Validar pontuação
    if request.pontuacao < 0 or request.pontuacao > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pontuação deve estar entre 0 e 10"
        )
    
    # Criar atividade (cada atividade tem ID único, mesmo que mesma categoria)
    nova_atividade = Atividade(
        categoria=request.categoria,
        titulo=None,  # Gerado no front
        descricao=None  # Gerado no front
    )
    try:
        db.add(nova_atividade)
        db.flush()  # Para obter o ID da atividade

        # Criar progresso
        novo_progresso = Progresso(
            pontuacao=request.pontuacao,
            observacoes=request.observacoes,
            concluida=True,  # Se chegou aqui, foi concluída
            crianca_id=request.crianca_id,
            atividade_id=nova_atividade.id,
            usuario_id=current_user.id  # Professor logado
        )
        db.add(novo_progresso)
        db.commit()
        db.refresh(novo_progresso)
        return novo_progresso
    except IntegrityError as e:
        db.rollback()
        # FK violation or not-null constraint
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database integrity error: {e.orig if hasattr(e, 'orig') else str(e)}")
    except ProgrammingError as e:
        db.rollback()
        # Likely missing table / schema mismatch
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database programming error: {e.orig if hasattr(e, 'orig') else str(e)}")
    except OperationalError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operational error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


@router.post("/registrar", response_model=ProgressoResponse, status_code=status.HTTP_201_CREATED)
def registrar_progresso(
    progresso_data: ProgressoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registrar progresso usando atividade existente
    
    Front-end envia: crianca_id, atividade_id, pontuacao, observacoes, concluida
    usuario_id é preenchido automaticamente do token JWT
    """
    # Front-end NÃO envia usuario_id, então preenchemos automaticamente do token
    progresso_dict = progresso_data.dict(exclude_unset=True)
    progresso_dict['usuario_id'] = current_user.id  # Sempre usar o usuário do token
    
    new_progresso = Progresso(**progresso_dict)
    try:
        db.add(new_progresso)
        db.commit()
        db.refresh(new_progresso)
        return new_progresso
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database integrity error: {e.orig if hasattr(e, 'orig') else str(e)}")
    except ProgrammingError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database programming error: {e.orig if hasattr(e, 'orig') else str(e)}")
    except OperationalError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operational error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


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
