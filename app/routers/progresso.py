from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from app.database import get_db
from app.models.progresso import Progresso
from app.models.atividade import Atividade
from app.models.crianca import Crianca
from app.models.turma import Turma
from app.schemas.progresso import ProgressoCreate, ProgressoResponse, ProgressoUpdate, ProgressoResumo
from app.schemas.atividade import AtividadeCreate
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError

router = APIRouter(prefix="/progresso", tags=["Progresso"])

# Logger para debug temporário em produção (remover depois de investigado)
logger = logging.getLogger("funny.progresso")
logger.setLevel(logging.INFO)


class RegistrarMiniJogoRequest(BaseModel):
    """Request para registrar um mini-jogo completo
    O front roda o mini-jogo e envia apenas: nota, categoria e aluno
    """
    pontuacao: int = Field(..., ge=0, le=10, description="Pontuação obtida no mini-jogo (0 a 10)")
    categoria: str = Field(..., description="Categoria do mini-jogo: Matemáticas, Português, Lógica ou Cotidiano")
    crianca_id: int = Field(..., description="ID do aluno que realizou o mini-jogo")
    titulo: str = Field(..., description="Título da atividade gerada (deve ser enviado pelo front)")
    descricao: str = Field(..., description="Descrição da atividade gerada (deve ser enviada pelo front)")
    observacoes: Optional[str] = Field(None, description="Observações opcionais sobre o desempenho")


@router.post("/registrar-minijogo", response_model=ProgressoResponse)
def registrar_minijogo(
    request: RegistrarMiniJogoRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registrar resultado de um mini-jogo completo
    
    Este endpoint é usado quando o front-end termina de rodar um mini-jogo.
    Busca ou cria a atividade (mesmo título + categoria = mesma atividade) e 
    atualiza ou cria o progresso (mesma criança + atividade = atualiza progresso existente).
    
    - **pontuacao**: Nota obtida (0 a 10)
    - **categoria**: Matemáticas, Português, Lógica ou Cotidiano
    - **crianca_id**: ID do aluno que realizou
    - **titulo**: Título da atividade (ex: "Jogo da Memória", "Família de Palavras")
    - **descricao**: Descrição da atividade
    - **observacoes**: Observações opcionais
    - **responsavel_id**: Automático (determinado a partir da turma/criança)
    
    Comportamento:
    - Se a atividade (título + categoria) já existe, reutiliza ela
    - Se o progresso (criança + atividade) já existe, atualiza ao invés de criar novo
    - Retorna 200 (OK) se atualizou, 201 (Created) se criou novo
    """
    # Log payload para debug (temporário)
    try:
        logger.info(f"registrar_minijogo payload: {request.dict()}")
    except Exception:
        logger.info("registrar_minijogo: unable to log payload")

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
    
    try:
        # Buscar ou criar atividade (mesmo título e categoria = mesma atividade)
        atividade_existente = db.query(Atividade).filter(
            Atividade.titulo == request.titulo,
            Atividade.categoria == request.categoria
        ).first()
        
        if atividade_existente:
            # Usar atividade existente
            atividade = atividade_existente
        else:
            # Criar nova atividade apenas se não existir
            nova_atividade = Atividade(
                categoria=request.categoria,
                titulo=request.titulo,
                descricao=request.descricao,
                nivel_dificuldade=1,
            )
            db.add(nova_atividade)
            db.flush()  # Para obter o ID da atividade
            atividade = nova_atividade

        # Determine responsavel_id from the child's turma (if available)
        crianca = db.query(Crianca).filter(Crianca.id == request.crianca_id).first()
        if not crianca:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Criança não encontrada")

        turma = None
        responsavel_id = None
        if crianca.turma_id is not None:
            turma = db.query(Turma).filter(Turma.id == crianca.turma_id).first()
            if turma:
                responsavel_id = turma.responsavel_id

        # Verificar se já existe progresso para esta criança + atividade
        progresso_existente = db.query(Progresso).filter(
            Progresso.crianca_id == request.crianca_id,
            Progresso.atividade_id == atividade.id
        ).first()

        if progresso_existente:
            # Atualizar progresso existente ao invés de criar novo
            progresso_existente.pontuacao = request.pontuacao
            progresso_existente.observacoes = request.observacoes
            progresso_existente.concluida = True
            progresso_existente.responsavel_id = responsavel_id
            db.add(progresso_existente)
            db.commit()
            db.refresh(progresso_existente)
            # Retornar 200 (OK) para atualização
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(progresso_existente))
        else:
            # Criar novo progresso apenas se não existir
            novo_progresso = Progresso(
                pontuacao=request.pontuacao,
                observacoes=request.observacoes,
                concluida=True,  # Se chegou aqui, foi concluída
                crianca_id=request.crianca_id,
                atividade_id=atividade.id,
                responsavel_id=responsavel_id
            )
            db.add(novo_progresso)
            db.commit()
            db.refresh(novo_progresso)
            # Retornar 201 (Created) para criação
            return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(novo_progresso))
    except IntegrityError as e:
        db.rollback()
        # FK violation or not-null constraint
        logger.exception("IntegrityError in registrar_minijogo")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database integrity error: {e.orig if hasattr(e, 'orig') else str(e)}")
    except ProgrammingError as e:
        db.rollback()
        # Likely missing table / schema mismatch
        logger.exception("ProgrammingError in registrar_minijogo")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database programming error: {e.orig if hasattr(e, 'orig') else str(e)}")
    except OperationalError as e:
        db.rollback()
        logger.exception("OperationalError in registrar_minijogo")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operational error: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in registrar_minijogo")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


@router.post("/registrar", response_model=ProgressoResponse)
def registrar_progresso(
    progresso_data: ProgressoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registrar progresso usando atividade existente
    
    Front-end envia: crianca_id, atividade_id, pontuacao, observacoes, concluida
    responsavel_id é determinado automaticamente a partir da criança/turma
    """
    # Log payload para debug (temporário)
    try:
        logger.info(f"registrar_progresso payload: {progresso_data.dict(exclude_unset=True)}")
    except Exception:
        logger.info("registrar_progresso: unable to log payload")

    # Front-end NÃO envia responsavel_id; determinamos a responsavel_id a partir da criança/turma
    progresso_dict = progresso_data.dict(exclude_unset=True)
    crianca_id = progresso_dict.get('crianca_id')
    responsavel_id = None
    if crianca_id is not None:
        crianca = db.query(Crianca).filter(Crianca.id == crianca_id).first()
        if crianca:
            if crianca.turma_id is not None:
                turma = db.query(Turma).filter(Turma.id == crianca.turma_id).first()
                if turma:
                    responsavel_id = turma.responsavel_id
    progresso_dict['responsavel_id'] = responsavel_id
    
    # Try to find an existing progresso for this atividade + crianca
    # Com a mudança em registrar_minijogo, não deve haver múltiplos registros,
    # mas mantemos a busca para compatibilidade com dados antigos
    try:
        existing = db.query(Progresso).filter(
            Progresso.atividade_id == progresso_dict.get('atividade_id'),
            Progresso.crianca_id == progresso_dict.get('crianca_id')
        ).first()  # Removido order_by pois não deve haver múltiplos

        if existing:
            # Update the existing progresso instead of creating a duplicate
            existing.pontuacao = progresso_dict.get('pontuacao', existing.pontuacao)
            existing.observacoes = progresso_dict.get('observacoes', existing.observacoes)
            existing.concluida = progresso_dict.get('concluida', existing.concluida)
            # Keep/update responsavel association from child's turma
            existing.responsavel_id = progresso_dict.get('responsavel_id', existing.responsavel_id)
            db.add(existing)
            db.commit()
            db.refresh(existing)
            # Retornar 200 (OK) para atualização
            return JSONResponse(status_code=status.HTTP_200_OK, content=jsonable_encoder(existing))

        # No existing progresso found -> create a new one
        new_progresso = Progresso(**progresso_dict)
        db.add(new_progresso)
        db.commit()
        db.refresh(new_progresso)
        # return created with 201
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(new_progresso))
    except IntegrityError as e:
        db.rollback()
        logger.exception("IntegrityError in registrar_progresso")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database integrity error: {e.orig if hasattr(e, 'orig') else str(e)}")
    except ProgrammingError as e:
        db.rollback()
        logger.exception("ProgrammingError in registrar_progresso")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database programming error: {e.orig if hasattr(e, 'orig') else str(e)}")
    except OperationalError as e:
        db.rollback()
        logger.exception("OperationalError in registrar_progresso")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operational error: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.exception("Unexpected error in registrar_progresso")
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
