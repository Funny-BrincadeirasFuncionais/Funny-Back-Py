from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class RelatorioCriancaRequest(BaseModel):
    """Schema para solicitação de relatório individual de criança"""
    crianca_id: int
    incluir_progresso: bool = True
    incluir_atividades: bool = True
    periodo_dias: Optional[int] = None  # Se None, inclui todo o histórico


class RelatorioTurmaRequest(BaseModel):
    """Schema para solicitação de relatório de turma"""
    turma_id: Optional[int] = None  # Se None, analisa todas as turmas (compatibilidade retroativa)
    incluir_progresso: bool = True
    incluir_atividades: bool = True
    periodo_dias: Optional[int] = None  # Se None, inclui todo o histórico


class RelatorioCriancaResponse(BaseModel):
    """Schema para resposta do relatório individual de criança"""
    crianca_id: int
    nome_crianca: str
    idade: int
    diagnostico: str
    
    # Campos estruturados (fechados)
    resumo_geral: Dict[str, Any]  # Contém: media_pontuacao, taxa_sucesso, total_mini_jogos
    desempenho_por_categoria: Dict[str, Any]  # Desempenho por categoria de mini-jogo (Matemáticas, Português, Lógica, Cotidiano)
    
    # Campos abertos (texto livre)
    resumo: str  # Resumo executivo do relatório
    
    # Metadados
    data_geracao: datetime
    periodo_analisado: Optional[str] = None


class RelatorioTurmaResponse(BaseModel):
    """Schema para resposta do relatório de turma"""
    total_criancas: int
    
    # Campos estruturados (fechados)
    resumo_geral_turma: Dict[str, Any]  # Contém: total_atividades
    distribuicao_diagnosticos: Dict[str, int]
    performance_media: Dict[str, Any]  # Contém: pontuacao_media, taxa_conclusao
    atividades_mais_efetivas: List[Dict[str, Any]]  # Contém: titulo, categoria, media_pontuacao
    
    # Campos abertos (texto livre)
    resumo: str  # Resumo executivo do relatório da turma
    
    # Metadados
    data_geracao: datetime
    periodo_analisado: Optional[str] = None


class DadosCriancaParaIA(BaseModel):
    """Schema para dados da criança que serão enviados para a IA"""
    id: int
    nome: str
    idade: int
    diagnostico: str
    progressos: List[Dict[str, Any]]
    atividades_realizadas: List[Dict[str, Any]]
    resumo_estatisticas: Dict[str, Any]


class DadosTurmaParaIA(BaseModel):
    """Schema para dados da turma que serão enviados para a IA"""
    total_criancas: int
    criancas: List[DadosCriancaParaIA]
    estatisticas_gerais: Dict[str, Any]
    atividades_disponiveis: List[Dict[str, Any]]
