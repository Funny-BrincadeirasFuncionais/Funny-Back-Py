from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, responsaveis, diagnosticos, criancas, atividades, progresso

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para gestão de atividades terapêuticas para crianças com necessidades especiais",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(responsaveis.router)
app.include_router(diagnosticos.router)
app.include_router(criancas.router)
app.include_router(atividades.router)
app.include_router(progresso.router)


@app.get("/")
def root():
    """Endpoint raiz da API"""
    return {
        "message": "🚀 API está funcionando!",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Endpoint de verificação de saúde da API"""
    return {"status": "healthy", "message": "API funcionando corretamente"}
