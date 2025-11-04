# Correções Aplicadas - Backend Database

## Problemas Identificados

1. **Dados desaparecendo ao reiniciar a API**
   - SQLite estava sendo usado ao invés de PostgreSQL
   - `Base.metadata.create_all()` causava conflito de tabelas
   - Migrations do Alembic não estavam sendo aplicadas

2. **Erros no Deploy no Render**
   - `alembic: command not found` - pacote não instalado
   - `sqlite3.OperationalError` - banco errado sendo usado
   - `table usuarios already exists` - conflito de schema

## Soluções Implementadas

### 1. requirements.txt
**Adicionado:**
```
alembic==1.12.1
openai==1.3.0
```

### 2. app/main.py
**Removido:**
```python
Base.metadata.create_all(bind=engine)
```
**Motivo:** O Alembic gerencia o schema, não o SQLAlchemy diretamente.

### 3. entrypoint.sh
**Melhorias:**
- Aguarda PostgreSQL estar pronto (10 tentativas)
- Verifica se comando `alembic` existe antes de usar
- Logging melhorado para debug
- Fallback para porta 10000 se PORT não definida

### 4. alembic/env.py
**Atualizado get_url():**
```python
def get_url():
    # Prioriza DATABASE_URL do Render (completa)
    url = os.getenv("DATABASE_URL")
    if url:
        # Converte postgres:// para postgresql:// (SQLAlchemy 1.4+)
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    
    # Fallback para variáveis individuais (desenvolvimento local)
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME", "funny_db")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"
```

### 5. alembic/versions/0001_initial_schema.py
**Criada migration inicial com todas as tabelas:**
- `usuarios` - Usuários do sistema
- `responsaveis` - Professores/Responsáveis
- `diagnosticos` - Diagnósticos das crianças
- `turmas` - Classes/Turmas
- `criancas` - Crianças cadastradas
- `atividades` - Atividades/Jogos
- `progresso` - Registros de progresso

## Fluxo de Deploy no Render

1. **Build:**
   ```bash
   pip install -r requirements.txt
   ```
   - Agora inclui `alembic==1.12.1`

2. **Entrypoint (entrypoint.sh):**
   ```bash
   # Aguarda PostgreSQL
   for i in {1..10}; do
       if pg_isready -h $db_host -p ${db_port:-5432}; then
           break
       fi
       sleep 2
   done
   
   # Roda migrations se alembic disponível
   if command -v alembic >/dev/null 2>&1; then
       alembic upgrade head
   fi
   
   # Inicia servidor
   gunicorn app.main:app --bind 0.0.0.0:${PORT:-10000}
   ```

3. **Alembic cria tabelas:**
   - Lê `DATABASE_URL` do ambiente Render
   - Executa `alembic upgrade head`
   - Aplica migration `0001_initial_schema.py`
   - Cria todas as tabelas no PostgreSQL

4. **Aplicação inicia:**
   - `app/main.py` não tenta mais criar tabelas
   - SQLAlchemy conecta ao PostgreSQL via `DATABASE_URL`
   - Dados são persistidos corretamente

## Variáveis de Ambiente Necessárias no Render

### Obrigatórias:
- `DATABASE_URL` - URL completa do PostgreSQL (Render fornece automaticamente)
- `jwt_secret_key` - Chave secreta para JWT
- `openai_api_key` - API key da OpenAI

### Opcionais (para override):
- `db_host` - Host do banco
- `db_port` - Porta do banco
- `db_name` - Nome do banco
- `db_user` - Usuário do banco
- `db_password` - Senha do banco

## Testando Localmente

```bash
# 1. Configurar variável de ambiente
export DATABASE_URL="postgresql://user:password@localhost:5432/funny_db"

# 2. Rodar migrations
cd Funny-Back/Funny-Back-Py
alembic upgrade head

# 3. Iniciar servidor
python run.py
```

## Próximos Passos

1. **Commit e Push:**
   ```bash
   git add .
   git commit -m "Fix: Corrige persistência de dados no PostgreSQL com Alembic migrations"
   git push
   ```

2. **Monitorar Logs no Render:**
   - Verificar se `alembic upgrade head` executa sem erros
   - Confirmar que não há mais erros de SQLite
   - Confirmar que tabelas são criadas corretamente

3. **Testar Persistência:**
   - Criar alguns dados via API
   - Reiniciar o serviço no Render
   - Verificar se dados ainda existem

## Estrutura do Banco de Dados

```
usuarios (id, nome, email, senha_hash)
    ↓
responsaveis (id, nome, email, telefone, turmas)
    ↓
turmas (id, nome, responsavel_id)
    ↓
criancas (id, nome, idade, diagnostico_id, turma_id)
    ↓
progresso (id, crianca_id, atividade_id, pontuacao, data_realizacao, observacoes, concluida)
    ↑
atividades (id, titulo, descricao, categoria, nivel_dificuldade)
    ↑
diagnosticos (id, tipo, descricao)
```

## Observações Importantes

- ✅ Alembic agora gerencia completamente o schema do banco
- ✅ `Base.metadata.create_all()` removido (causava conflitos)
- ✅ `DATABASE_URL` do Render é usado corretamente
- ✅ Conversão `postgres://` → `postgresql://` para SQLAlchemy 1.4+
- ✅ Migration inicial cria todas as tabelas e índices
- ✅ Suporte a rollback (`alembic downgrade -1`)

## Comandos Úteis

```bash
# Ver histórico de migrations
alembic history

# Ver migrations aplicadas
alembic current

# Criar nova migration
alembic revision --autogenerate -m "descrição"

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1
```
