# Funny Backend API - FastAPI

Sistema de gestão de atividades terapêuticas para crianças com necessidades especiais, desenvolvido em Python com FastAPI.

## 🚀 Funcionalidades

- **Autenticação JWT** - Sistema seguro de login e registro
- **Gestão de Responsáveis** - CRUD completo para responsáveis
- **Gestão de Crianças** - Cadastro e acompanhamento de crianças
- **Diagnósticos** - Tipos de diagnósticos médicos
- **Atividades Terapêuticas** - Atividades com diferentes níveis de dificuldade
- **Acompanhamento de Progresso** - Registro e relatórios de progresso
- **Documentação Automática** - Swagger/OpenAPI integrado

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL
- pip

## 🛠️ Instalação

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd funny-back-py
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Configure o banco de dados**
```bash
# Crie o banco PostgreSQL
createdb funny_db

# Execute as migrações (opcional - as tabelas são criadas automaticamente)
alembic upgrade head
```

## 🚀 Executando a Aplicação

```bash
# Modo desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Modo produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 Estrutura do Projeto

```
funny-back-py/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação principal
│   ├── config.py            # Configurações
│   ├── database.py          # Configuração do banco
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── usuario.py
│   │   ├── responsavel.py
│   │   ├── crianca.py
│   │   ├── diagnostico.py
│   │   ├── atividade.py
│   │   └── progresso.py
│   ├── schemas/             # Schemas Pydantic
│   │   ├── usuario.py
│   │   ├── responsavel.py
│   │   ├── crianca.py
│   │   ├── diagnostico.py
│   │   ├── atividade.py
│   │   └── progresso.py
│   ├── routers/             # Rotas da API
│   │   ├── auth.py
│   │   ├── responsaveis.py
│   │   ├── criancas.py
│   │   ├── diagnosticos.py
│   │   ├── atividades.py
│   │   └── progresso.py
│   └── auth/                # Sistema de autenticação
│       ├── jwt_handler.py
│       ├── password_handler.py
│       └── dependencies.py
├── alembic/                 # Migrações do banco
├── requirements.txt
├── env.example
└── README.md
```

## 🔐 Autenticação

A API usa JWT (JSON Web Tokens) para autenticação. Para acessar rotas protegidas:

1. **Registre um usuário**:
```bash
POST /auth/register
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "senha123"
}
```

2. **Faça login**:
```bash
POST /auth/login
{
  "email": "joao@email.com",
  "senha": "senha123"
}
```

3. **Use o token** nas requisições:
```bash
Authorization: Bearer <seu_token>
```

## 📊 Endpoints Principais

### Autenticação
- `POST /auth/register` - Registrar usuário
- `POST /auth/login` - Login

### Responsáveis
- `GET /responsaveis` - Listar responsáveis
- `POST /responsaveis` - Criar responsável
- `GET /responsaveis/{id}` - Buscar responsável
- `PUT /responsaveis/{id}` - Atualizar responsável
- `DELETE /responsaveis/{id}` - Deletar responsável

### Crianças
- `GET /criancas` - Listar crianças
- `POST /criancas` - Criar criança
- `GET /criancas/{id}` - Buscar criança
- `PUT /criancas/{id}` - Atualizar criança
- `DELETE /criancas/{id}` - Deletar criança

### Atividades
- `GET /atividades` - Listar atividades
- `POST /atividades` - Criar atividade
- `GET /atividades/{id}` - Buscar atividade
- `PUT /atividades/{id}` - Atualizar atividade
- `DELETE /atividades/{id}` - Deletar atividade

### Progresso
- `POST /progresso/registrar` - Registrar progresso
- `GET /progresso/crianca/{id}` - Progresso de uma criança
- `GET /progresso/atividade/{id}` - Progresso de uma atividade
- `GET /progresso/crianca/{id}/resumo` - Resumo do progresso

## 🔧 Configuração

### Variáveis de Ambiente

```env
# Database
DB_NAME=funny_db
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_SECRET_KEY=sua_chave_secreta_jwt
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120

# App
APP_NAME=Funny Backend API
APP_VERSION=1.0.0
DEBUG=True
```

## 🧪 Testando a API

Use a documentação interativa em `/docs` ou ferramentas como Postman/Insomnia.

### Exemplo de uso com curl:

```bash
# Registrar usuário
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"nome": "João Silva", "email": "joao@email.com", "senha": "senha123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@email.com", "senha": "senha123"}'

# Criar responsável (com token)
curl -X POST "http://localhost:8000/responsaveis" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <seu_token>" \
  -d '{"nome": "Maria Silva", "email": "maria@email.com", "telefone": "11999999999"}'
```

## 🚀 Deploy

Para deploy em produção:

1. Configure as variáveis de ambiente
2. Use um servidor WSGI como Gunicorn:
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

3. Configure um proxy reverso (Nginx)
4. Use HTTPS em produção

## 📝 Melhorias Implementadas

- ✅ **FastAPI** com documentação automática
- ✅ **Pydantic** para validação de dados
- ✅ **SQLAlchemy** como ORM moderno
- ✅ **JWT** com configuração segura
- ✅ **Middleware de autenticação** adequado
- ✅ **Tratamento de erros** robusto
- ✅ **Validação de dados** completa
- ✅ **Estrutura modular** e escalável
- ✅ **Type hints** em todo o código
- ✅ **CORS** configurado
- ✅ **Health check** endpoint

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.