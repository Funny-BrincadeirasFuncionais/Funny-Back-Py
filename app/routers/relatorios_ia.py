from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario
from app.schemas.relatorio_ia import (
    RelatorioCriancaRequest,
    RelatorioTurmaRequest,
    RelatorioCriancaResponse,
    RelatorioTurmaResponse
)
from app.services.ai_service import ai_service

router = APIRouter(prefix="/relatorios-ia", tags=["Relatórios IA"])


@router.post("/crianca", response_model=RelatorioCriancaResponse)
async def gerar_relatorio_crianca(
    request: RelatorioCriancaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera relatório individual de uma criança usando IA
    
    - **crianca_id**: ID da criança para análise
    - **incluir_progresso**: Se deve incluir dados de progresso (padrão: True)
    - **incluir_atividades**: Se deve incluir dados de atividades (padrão: True)
    - **periodo_dias**: Número de dias para análise (opcional, se não informado analisa todo histórico)
    """
    try:
        relatorio = await ai_service.gerar_relatorio_crianca(
            db=db,
            crianca_id=request.crianca_id,
            periodo_dias=request.periodo_dias
        )
        return relatorio
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório: {str(e)}"
        )


@router.post("/turma", response_model=RelatorioTurmaResponse)
async def gerar_relatorio_turma(
    request: RelatorioTurmaRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Gera relatório da turma usando IA
    
    - **turma_id**: ID da turma para análise (opcional, se não informado analisa todas as turmas)
    - **incluir_progresso**: Se deve incluir dados de progresso (padrão: True)
    - **incluir_atividades**: Se deve incluir dados de atividades (padrão: True)
    - **periodo_dias**: Número de dias para análise (opcional, se não informado analisa todo histórico)
    """
    try:
        relatorio = await ai_service.gerar_relatorio_turma(
            db=db,
            turma_id=request.turma_id,
            periodo_dias=request.periodo_dias
        )
        return relatorio
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar relatório da turma: {str(e)}"
        )


@router.get("/crianca/{crianca_id}/preview")
async def preview_dados_crianca(
    crianca_id: int,
    periodo_dias: int = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Visualiza os dados que serão enviados para a IA (útil para debug)
    """
    try:
        dados = ai_service._prepare_crianca_data(db, crianca_id, periodo_dias)
        return {
            "crianca_id": crianca_id,
            "dados_preparados": dados.dict(),
            "total_progressos": len(dados.progressos),
            "total_atividades": len(dados.atividades_realizadas)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao preparar dados: {str(e)}"
        )


@router.get("/turma/preview")
async def preview_dados_turma(
    turma_id: int = None,
    periodo_dias: int = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Visualiza os dados da turma que serão enviados para a IA (útil para debug)
    """
    try:
        dados = ai_service._prepare_turma_data(db, turma_id=turma_id, periodo_dias=periodo_dias)
        return {
            "total_criancas": dados.total_criancas,
            "dados_preparados": dados.dict(),
            "estatisticas_gerais": dados.estatisticas_gerais
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao preparar dados da turma: {str(e)}"
        )


@router.get("/health")
async def health_check_ai():
    """
    Verifica se o serviço de IA está configurado corretamente
    """
    # Verificar se a chave está configurada no AIService (que lê do settings ou env)
    api_key_configured = bool(ai_service.api_key)
    
    return {
        "status": "healthy" if api_key_configured else "misconfigured",
        "api_key_configured": api_key_configured,
        "model": ai_service.model,
        "message": "Serviço de IA configurado" if api_key_configured else "OPENAI_API_KEY não configurada"
    }
