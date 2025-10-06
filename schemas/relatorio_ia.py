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
    resumo_geral: Dict[str, Any]
    areas_desenvolvimento: Dict[str, Any]
    pontos_fortes: List[str]
    areas_melhoria: List[str]
    recomendacoes: List[str]
    
    # Campos abertos (texto livre)
    analise_detalhada: str
    observacoes_terapeuticas: str
    proximos_passos: str
    
    # Metadados
    data_geracao: datetime
    periodo_analisado: Optional[str] = None


class RelatorioTurmaResponse(BaseModel):
    """Schema para resposta do relatório de turma"""
    total_criancas: int
    
    # Campos estruturados (fechados)
    resumo_geral_turma: Dict[str, Any]
    distribuicao_diagnosticos: Dict[str, int]
    performance_media: Dict[str, float]
    atividades_mais_efetivas: List[Dict[str, Any]]
    areas_comuns_melhoria: List[str]
    recomendacoes_gerais: List[str]
    
    # Campos abertos (texto livre)
    analise_coletiva: str
    observacoes_pedagogicas: str
    estrategias_turma: str
    
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
