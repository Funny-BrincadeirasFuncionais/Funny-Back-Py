# Relatórios com IA - Funny Backend

## Visão Geral

Este módulo adiciona funcionalidades de IA ao backend da aplicação Funny, permitindo a geração de relatórios inteligentes sobre crianças individuais e turmas completas usando o modelo GPT-4o-mini da OpenAI.

## Funcionalidades

### 1. Relatório Individual de Criança
- **Endpoint**: `POST /relatorios-ia/crianca`
- **Descrição**: Gera um relatório detalhado sobre uma criança específica
- **Parâmetros**:
  - `crianca_id`: ID da criança
  - `incluir_progresso`: Se deve incluir dados de progresso (padrão: True)
  - `incluir_atividades`: Se deve incluir dados de atividades (padrão: True)
  - `periodo_dias`: Número de dias para análise (opcional)

### 2. Relatório de Turma
- **Endpoint**: `POST /relatorios-ia/turma`
- **Descrição**: Gera um relatório coletivo sobre toda a turma
- **Parâmetros**:
  - `incluir_progresso`: Se deve incluir dados de progresso (padrão: True)
  - `incluir_atividades`: Se deve incluir dados de atividades (padrão: True)
  - `periodo_dias`: Número de dias para análise (opcional)

### 3. Endpoints de Debug
- **Preview dados criança**: `GET /relatorios-ia/crianca/{crianca_id}/preview`
- **Preview dados turma**: `GET /relatorios-ia/turma/preview`
- **Health check**: `GET /relatorios-ia/health`

## Estrutura dos Relatórios

### Relatório Individual
```json
{
  "crianca_id": 1,
  "nome_crianca": "João",
  "idade": 8,
  "diagnostico": "TEA",
  "resumo_geral": {
    "total_atividades": 15,
    "taxa_sucesso": 85.5
  },
  "areas_desenvolvimento": {
    "cognitiva": "Bom desenvolvimento",
    "motora": "Necessita atenção",
    "social": "Em progresso",
    "linguagem": "Avançando bem"
  },
  "pontos_fortes": ["Concentração", "Memória"],
  "areas_melhoria": ["Interação social", "Coordenação motora"],
  "recomendacoes": ["Atividades em grupo", "Exercícios motores"],
  "analise_detalhada": "Texto longo com análise detalhada...",
  "observacoes_terapeuticas": "Observações técnicas...",
  "proximos_passos": "Próximos passos sugeridos...",
  "data_geracao": "2024-01-15T10:30:00",
  "periodo_analisado": "Últimos 30 dias"
}
```

### Relatório de Turma
```json
{
  "total_criancas": 12,
  "resumo_geral_turma": {
    "performance_media": 78.5,
    "engajamento_geral": "Alto"
  },
  "distribuicao_diagnosticos": {
    "TEA": 5,
    "TDAH": 4,
    "Síndrome de Down": 3
  },
  "performance_media": {
    "pontuacao_media": 78.5,
    "taxa_conclusao": 82.3
  },
  "atividades_mais_efetivas": [
    {
      "atividade": "Quebra-cabeça",
      "categoria": "Cognitiva",
      "efetividade": "Alta"
    }
  ],
  "areas_comuns_melhoria": ["Interação social", "Coordenação"],
  "recomendacoes_gerais": ["Atividades em grupo", "Reforço positivo"],
  "analise_coletiva": "Análise da turma...",
  "observacoes_pedagogicas": "Observações pedagógicas...",
  "estrategias_turma": "Estratégias para a turma...",
  "data_geracao": "2024-01-15T10:30:00",
  "periodo_analisado": "Últimos 30 dias"
}
```

## Configuração

### 1. Variáveis de Ambiente
Adicione ao seu arquivo `.env`:
```
OPENAI_API_KEY=sua_chave_da_openai_aqui
```

### 2. Instalação de Dependências
```bash
pip install -r requirements.txt
```

### 3. Dependências Adicionadas
- `httpx==0.25.2`: Para requisições HTTP assíncronas
- `openai==1.3.0`: SDK oficial da OpenAI

## Uso

### Exemplo de Relatório Individual
```python
import requests

# Dados da requisição
data = {
    "crianca_id": 1,
    "incluir_progresso": True,
    "incluir_atividades": True,
    "periodo_dias": 30
}

# Fazer requisição
response = requests.post(
    "http://localhost:8000/relatorios-ia/crianca",
    json=data,
    headers={"Authorization": "Bearer seu_token_aqui"}
)

relatorio = response.json()
```

### Exemplo de Relatório de Turma
```python
import requests

# Dados da requisição
data = {
    "incluir_progresso": True,
    "incluir_atividades": True,
    "periodo_dias": 30
}

# Fazer requisição
response = requests.post(
    "http://localhost:8000/relatorios-ia/turma",
    json=data,
    headers={"Authorization": "Bearer seu_token_aqui"}
)

relatorio = response.json()
```

## Características Técnicas

### Modelo de IA
- **Modelo**: GPT-4o-mini (mais recente e eficiente)
- **Formato de Resposta**: JSON estruturado
- **Temperatura**: 0.7 (balanceamento entre criatividade e consistência)
- **Max Tokens**: 2000

### Estrutura de Dados
- **Campos Fechados**: Dados estruturados (números, listas, objetos)
- **Campos Abertos**: Texto livre para análises detalhadas
- **Metadados**: Data de geração, período analisado

### Segurança
- Autenticação JWT obrigatória
- Validação de dados de entrada
- Tratamento de erros robusto
- Timeout de 30 segundos para requisições à OpenAI

## Monitoramento

### Health Check
```bash
curl http://localhost:8000/relatorios-ia/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "model": "gpt-4o-mini",
  "message": "Serviço de IA configurado"
}
```

### Preview de Dados
Use os endpoints de preview para verificar os dados que serão enviados para a IA antes de gerar o relatório completo.

## Limitações e Considerações

1. **Custos**: Cada relatório consome tokens da OpenAI
2. **Latência**: Relatórios podem levar alguns segundos para serem gerados
3. **Dependência**: Requer conexão com a internet e chave válida da OpenAI
4. **Rate Limits**: Respeita os limites de taxa da API da OpenAI

## Troubleshooting

### Erro: "OPENAI_API_KEY não configurada"
- Verifique se a variável de ambiente está definida
- Reinicie o servidor após adicionar a variável

### Erro: "Erro ao gerar relatório"
- Verifique a conectividade com a internet
- Confirme se a chave da API é válida
- Verifique se há dados suficientes para análise

### Timeout
- Aumente o timeout se necessário
- Verifique a estabilidade da conexão
