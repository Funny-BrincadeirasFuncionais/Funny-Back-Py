import os
import json
import httpx
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.crianca import Crianca
from app.models.progresso import Progresso
from app.models.atividade import Atividade
from app.models.turma import Turma
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
        self.model = "gpt-4o-mini"  # Modelo OpenAI disponível (gpt-5-mini não existe ainda)
        
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
                timeout=120.0  # Timeout aumentado para 2 minutos (OpenAI pode demorar)
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
                "pontuacao": progresso.pontuacao,  # Pontuação de 0 a 10
                "concluida": progresso.concluida,
                "observacoes": progresso.observacoes,
                "atividade_titulo": progresso.atividade.titulo if progresso.atividade else None,
                "atividade_categoria": progresso.atividade.categoria if progresso.atividade else None  # Matemáticas, Português, Lógica ou Cotidiano
            })
        
        # Calcular estatísticas
        total_progressos = len(progressos)
        progressos_concluidos = sum(1 for p in progressos if p.concluida)
        media_pontuacao = sum(p.pontuacao for p in progressos) / total_progressos if total_progressos > 0 else 0
        
        # Estatísticas por categoria de mini-jogo
        pontuacao_por_categoria = {}
        for progresso in progressos:
            if progresso.atividade:
                categoria = progresso.atividade.categoria
                if categoria not in pontuacao_por_categoria:
                    pontuacao_por_categoria[categoria] = []
                pontuacao_por_categoria[categoria].append(progresso.pontuacao)
        
        media_por_categoria = {
            cat: sum(ponts) / len(ponts) if len(ponts) > 0 else 0
            for cat, ponts in pontuacao_por_categoria.items()
        }
        
        # Buscar atividades realizadas (mini-jogos)
        atividades_ids = list(set(p.atividade_id for p in progressos if p.atividade_id))
        atividades = db.query(Atividade).filter(Atividade.id.in_(atividades_ids)).all()
        
        atividades_data = []
        for atividade in atividades:
            atividades_data.append({
                "id": atividade.id,
                "titulo": atividade.titulo,
                "descricao": atividade.descricao,
                "categoria": atividade.categoria  # Matemáticas, Português, Lógica ou Cotidiano
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
                "pontuacao_minima": min((p.pontuacao for p in progressos), default=0),
                "media_por_categoria": {cat: round(media, 2) for cat, media in media_por_categoria.items()},
                "total_mini_jogos_jogados": total_progressos
            }
        )
    
    def _prepare_turma_data(self, db: Session, turma_id: int = None, periodo_dias: int = None) -> DadosTurmaParaIA:
        """Prepara dados da turma para análise pela IA"""
        # Validar turma se turma_id fornecido
        if turma_id:
            turma = db.query(Turma).filter(Turma.id == turma_id).first()
            if not turma:
                raise ValueError(f"Turma com ID {turma_id} não encontrada")
            # Buscar crianças da turma específica
            criancas = db.query(Crianca).filter(Crianca.turma_id == turma_id).all()
        else:
            # Se não especificado, buscar todas (compatibilidade retroativa)
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
        
        # Buscar atividades disponíveis (mini-jogos)
        # Se há turma específica, buscar IDs de atividades realizadas pelas crianças da turma
        if turma_id and criancas:
            # Coletar IDs de atividades das crianças da turma
            atividades_ids = set()
            for crianca in criancas:
                progressos_crianca = db.query(Progresso).filter(Progresso.crianca_id == crianca.id).all()
                for progresso in progressos_crianca:
                    if progresso.atividade_id:
                        atividades_ids.add(progresso.atividade_id)
            
            if atividades_ids:
                atividades = db.query(Atividade).filter(Atividade.id.in_(list(atividades_ids))).all()
            else:
                # Se não houver atividades, buscar todas (fallback)
                atividades = db.query(Atividade).all()
        else:
            # Buscar todas as atividades disponíveis
            atividades = db.query(Atividade).all()
        
        atividades_data = []
        for atividade in atividades:
            atividades_data.append({
                "id": atividade.id,
                "titulo": atividade.titulo,
                "categoria": atividade.categoria  # Matemáticas, Português, Lógica ou Cotidiano
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
        
        IMPORTANTE: As atividades são mini-jogos educativos com pontuação de 0 a 10. 
        As categorias dos mini-jogos são: Matemáticas, Português, Lógica ou Cotidiano.
        
        DADOS DA CRIANÇA:
        {dados_crianca.json()}
        
        Gere um relatório JSON com a seguinte estrutura:
        {{
            "resumo_geral": {{
                "total_mini_jogos": "number",
                "taxa_sucesso": "number",
                "media_pontuacao": "number (0-10)"
            }},
            "desempenho_por_categoria": {{
                "Matemáticas": "análise baseada nas pontuações dos mini-jogos de Matemáticas",
                "Português": "análise baseada nas pontuações dos mini-jogos de Português",
                "Lógica": "análise baseada nas pontuações dos mini-jogos de Lógica",
                "Cotidiano": "análise baseada nas pontuações dos mini-jogos de Cotidiano"
            }},
            "resumo": "resumo executivo curto (2-3 parágrafos) destacando os principais pontos do relatório"
        }}
        
        Seja específico, técnico mas acessível. Analise o desempenho da criança nos mini-jogos 
        considerando as pontuações (0-10) e as diferentes categorias. Baseie suas análises nos dados fornecidos.
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
            desempenho_por_categoria=relatorio_data.get("desempenho_por_categoria", {}),
            resumo=relatorio_data.get("resumo", ""),
            data_geracao=datetime.now(),
            periodo_analisado=f"Últimos {periodo_dias} dias" if periodo_dias else "Todo o histórico"
        )
    
    async def gerar_relatorio_turma(self, db: Session, turma_id: int = None, periodo_dias: int = None) -> RelatorioTurmaResponse:
        """Gera relatório da turma usando IA"""
        dados_turma = self._prepare_turma_data(db, turma_id=turma_id, periodo_dias=periodo_dias)
        
        prompt = f"""
        Você é um especialista em terapia ocupacional e desenvolvimento infantil. 
        Analise os dados da turma abaixo e gere um relatório estruturado em JSON.
        
        IMPORTANTE: As atividades são mini-jogos educativos com pontuação de 0 a 10. 
        As categorias dos mini-jogos são: Matemáticas, Português, Lógica ou Cotidiano.
        
        DADOS DA TURMA:
        {dados_turma.json()}
        
        Gere um relatório JSON com a seguinte estrutura:
        {{
            "resumo_geral_turma": {{
                "total_criancas": "number",
                "total_atividades": "number"
            }},
            "distribuicao_diagnosticos": {{"diagnostico1": "number", "diagnostico2": "number"}},
            "performance_media": {{
                "pontuacao_media": "number (0-10)",
                "taxa_conclusao": "number"
            }},
            "atividades_mais_efetivas": [
                {{"titulo": "string", "categoria": "string", "media_pontuacao": "number"}}
            ],
            "resumo": "resumo executivo curto (2-3 parágrafos) destacando os principais pontos do relatório da turma"
        }}
        
        Analise padrões coletivos nos mini-jogos, identifique necessidades comuns, 
        categorize por tipo de mini-jogo (Matemáticas, Português, Lógica, Cotidiano) 
        e sugira estratégias grupais baseadas no desempenho médio (0-10) da turma.
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
            resumo=relatorio_data.get("resumo", ""),
            data_geracao=datetime.now(),
            periodo_analisado=f"Últimos {periodo_dias} dias" if periodo_dias else "Todo o histórico"
        )


# Instância global do serviço
ai_service = AIService()
