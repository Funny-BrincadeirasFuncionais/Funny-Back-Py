import os
import json
import httpx
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.crianca import Crianca
from app.models.progresso import Progresso
from app.models.atividade import Atividade
from app.schemas.relatorio_ia import (
    DadosCriancaParaIA, 
    DadosTurmaParaIA,
    RelatorioCriancaResponse,
    RelatorioTurmaResponse
)
from app.config import settings


class AIService:
    """Serviço para integração com IA (GPT-5-mini)"""
    
    def __init__(self):
        self.api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-5-mini"  # Usando o modelo mais recente disponível
        
    async def _make_openai_request(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Faz requisição para a API do OpenAI"""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não configurada")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    
    def _prepare_crianca_data(self, db: Session, crianca_id: int, periodo_dias: int = None) -> DadosCriancaParaIA:
        """Prepara dados da criança para análise pela IA"""
        crianca = db.query(Crianca).filter(Crianca.id == crianca_id).first()
        if not crianca:
            raise ValueError(f"Criança com ID {crianca_id} não encontrada")
        
        # Buscar progressos
        query = db.query(Progresso).filter(Progresso.crianca_id == crianca_id)
        if periodo_dias:
            data_limite = datetime.now() - timedelta(days=periodo_dias)
            query = query.filter(Progresso.id >= 0)  # Ajustar conforme estrutura de data
        
        progressos = query.all()
        
        # Preparar dados dos progressos
        progressos_data = []
        for progresso in progressos:
            progressos_data.append({
                "id": progresso.id,
                "pontuacao": progresso.pontuacao,
                "concluida": progresso.concluida,
                "observacoes": progresso.observacoes,
                "atividade_titulo": progresso.atividade.titulo if progresso.atividade else None,
                "atividade_categoria": progresso.atividade.categoria if progresso.atividade else None,
                "nivel_dificuldade": progresso.atividade.nivel_dificuldade if progresso.atividade else None
            })
        
        # Calcular estatísticas
        total_progressos = len(progressos)
        progressos_concluidos = sum(1 for p in progressos if p.concluida)
        media_pontuacao = sum(p.pontuacao for p in progressos) / total_progressos if total_progressos > 0 else 0
        
        # Buscar atividades realizadas
        atividades_ids = list(set(p.atividade_id for p in progressos if p.atividade_id))
        atividades = db.query(Atividade).filter(Atividade.id.in_(atividades_ids)).all()
        
        atividades_data = []
        for atividade in atividades:
            atividades_data.append({
                "id": atividade.id,
                "titulo": atividade.titulo,
                "descricao": atividade.descricao,
                "categoria": atividade.categoria,
                "nivel_dificuldade": atividade.nivel_dificuldade
            })
        
        return DadosCriancaParaIA(
            id=crianca.id,
            nome=crianca.nome,
            idade=crianca.idade,
            diagnostico=crianca.diagnostico.tipo if crianca.diagnostico else "Não especificado",
            progressos=progressos_data,
            atividades_realizadas=atividades_data,
            resumo_estatisticas={
                "total_progressos": total_progressos,
                "progressos_concluidos": progressos_concluidos,
                "taxa_conclusao": (progressos_concluidos / total_progressos * 100) if total_progressos > 0 else 0,
                "media_pontuacao": round(media_pontuacao, 2),
                "pontuacao_maxima": max((p.pontuacao for p in progressos), default=0),
                "pontuacao_minima": min((p.pontuacao for p in progressos), default=0)
            }
        )
    
    def _prepare_turma_data(self, db: Session, periodo_dias: int = None) -> DadosTurmaParaIA:
        """Prepara dados da turma para análise pela IA"""
        # Buscar todas as crianças
        criancas = db.query(Crianca).all()
        
        dados_criancas = []
        for crianca in criancas:
            dados_crianca = self._prepare_crianca_data(db, crianca.id, periodo_dias)
            dados_criancas.append(dados_crianca)
        
        # Calcular estatísticas gerais
        total_criancas = len(criancas)
        diagnosticos = {}
        for crianca in criancas:
            if crianca.diagnostico:
                tipo = crianca.diagnostico.tipo
                diagnosticos[tipo] = diagnosticos.get(tipo, 0) + 1
        
        # Buscar todas as atividades disponíveis
        atividades = db.query(Atividade).all()
        atividades_data = []
        for atividade in atividades:
            atividades_data.append({
                "id": atividade.id,
                "titulo": atividade.titulo,
                "categoria": atividade.categoria,
                "nivel_dificuldade": atividade.nivel_dificuldade
            })
        
        return DadosTurmaParaIA(
            total_criancas=total_criancas,
            criancas=dados_criancas,
            estatisticas_gerais={
                "distribuicao_diagnosticos": diagnosticos,
                "total_atividades": len(atividades),
                "categorias_atividades": list(set(a.categoria for a in atividades))
            },
            atividades_disponiveis=atividades_data
        )
    
    async def gerar_relatorio_crianca(self, db: Session, crianca_id: int, periodo_dias: int = None) -> RelatorioCriancaResponse:
        """Gera relatório individual de uma criança usando IA"""
        dados_crianca = self._prepare_crianca_data(db, crianca_id, periodo_dias)
        
        prompt = f"""
        Você é um especialista em terapia ocupacional e desenvolvimento infantil. 
        Analise os dados da criança abaixo e gere um relatório estruturado em JSON.
        
        DADOS DA CRIANÇA:
        {dados_crianca.json()}
        
        Gere um relatório JSON com a seguinte estrutura:
        {{
            "resumo_geral": {{
                "nome": "string",
                "idade": "number",
                "diagnostico": "string",
                "periodo_analisado": "string",
                "total_atividades": "number",
                "taxa_sucesso": "number"
            }},
            "areas_desenvolvimento": {{
                "cognitiva": "string",
                "motora": "string", 
                "social": "string",
                "linguagem": "string"
            }},
            "pontos_fortes": ["string1", "string2", "string3"],
            "areas_melhoria": ["string1", "string2", "string3"],
            "recomendacoes": ["string1", "string2", "string3"],
            "analise_detalhada": "texto longo com análise detalhada",
            "observacoes_terapeuticas": "texto com observações técnicas",
            "proximos_passos": "texto com próximos passos sugeridos"
        }}
        
        Seja específico, técnico mas acessível, e baseie suas análises nos dados fornecidos.
        """
        
        messages = [
            {"role": "system", "content": "Você é um especialista em terapia ocupacional e desenvolvimento infantil."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self._make_openai_request(messages)
        relatorio_data = json.loads(response["choices"][0]["message"]["content"])
        
        return RelatorioCriancaResponse(
            crianca_id=crianca_id,
            nome_crianca=dados_crianca.nome,
            idade=dados_crianca.idade,
            diagnostico=dados_crianca.diagnostico,
            resumo_geral=relatorio_data["resumo_geral"],
            areas_desenvolvimento=relatorio_data["areas_desenvolvimento"],
            pontos_fortes=relatorio_data["pontos_fortes"],
            areas_melhoria=relatorio_data["areas_melhoria"],
            recomendacoes=relatorio_data["recomendacoes"],
            analise_detalhada=relatorio_data["analise_detalhada"],
            observacoes_terapeuticas=relatorio_data["observacoes_terapeuticas"],
            proximos_passos=relatorio_data["proximos_passos"],
            data_geracao=datetime.now(),
            periodo_analisado=f"Últimos {periodo_dias} dias" if periodo_dias else "Todo o histórico"
        )
    
    async def gerar_relatorio_turma(self, db: Session, periodo_dias: int = None) -> RelatorioTurmaResponse:
        """Gera relatório da turma usando IA"""
        dados_turma = self._prepare_turma_data(db, periodo_dias)
        
        prompt = f"""
        Você é um especialista em terapia ocupacional e desenvolvimento infantil. 
        Analise os dados da turma abaixo e gere um relatório estruturado em JSON.
        
        DADOS DA TURMA:
        {dados_turma.json()}
        
        Gere um relatório JSON com a seguinte estrutura:
        {{
            "resumo_geral_turma": {{
                "total_criancas": "number",
                "diversidade_diagnosticos": "string",
                "performance_media": "number",
                "engajamento_geral": "string"
            }},
            "distribuicao_diagnosticos": {{"diagnostico1": "number", "diagnostico2": "number"}},
            "performance_media": {{
                "pontuacao_media": "number",
                "taxa_conclusao": "number",
                "areas_mais_desenvolvidas": ["string1", "string2"]
            }},
            "atividades_mais_efetivas": [
                {{"atividade": "string", "categoria": "string", "efetividade": "string"}}
            ],
            "areas_comuns_melhoria": ["string1", "string2", "string3"],
            "recomendacoes_gerais": ["string1", "string2", "string3"],
            "analise_coletiva": "texto longo com análise da turma",
            "observacoes_pedagogicas": "texto com observações pedagógicas",
            "estrategias_turma": "texto com estratégias para a turma"
        }}
        
        Analise padrões coletivos, identifique necessidades comuns e sugira estratégias grupais.
        """
        
        messages = [
            {"role": "system", "content": "Você é um especialista em terapia ocupacional e desenvolvimento infantil."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self._make_openai_request(messages)
        relatorio_data = json.loads(response["choices"][0]["message"]["content"])
        
        return RelatorioTurmaResponse(
            total_criancas=dados_turma.total_criancas,
            resumo_geral_turma=relatorio_data["resumo_geral_turma"],
            distribuicao_diagnosticos=relatorio_data["distribuicao_diagnosticos"],
            performance_media=relatorio_data["performance_media"],
            atividades_mais_efetivas=relatorio_data["atividades_mais_efetivas"],
            areas_comuns_melhoria=relatorio_data["areas_comuns_melhoria"],
            recomendacoes_gerais=relatorio_data["recomendacoes_gerais"],
            analise_coletiva=relatorio_data["analise_coletiva"],
            observacoes_pedagogicas=relatorio_data["observacoes_pedagogicas"],
            estrategias_turma=relatorio_data["estrategias_turma"],
            data_geracao=datetime.now(),
            periodo_analisado=f"Últimos {periodo_dias} dias" if periodo_dias else "Todo o histórico"
        )


# Instância global do serviço
ai_service = AIService()
