from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, turmas, responsaveis, diagnosticos, criancas, atividades, progresso, relatorios_ia, recaptcha
import sys
import traceback
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, ProgrammingError

# NÃO criar tabelas aqui - Alembic vai gerenciar as migrations
# Base.metadata.create_all(bind=engine)  # ❌ REMOVIDO

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API para gestão de atividades terapêuticas para crianças com necessidades especiais",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Log de inicialização para debug
print(f"🚀 Iniciando {settings.app_name} v{settings.app_version}", file=sys.stderr)
print(f"🔧 Engine configurado: {engine.url}", file=sys.stderr)

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
app.include_router(relatorios_ia.router)
app.include_router(turmas.router)
app.include_router(recaptcha.router)


@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
    """Return a JSON error for common DB integrity issues (FK violations, not-null)."""
    # Log full traceback server-side for debugging
    print("[IntegrityError]", exc, file=sys.stderr)
    try:
        detail = str(exc.orig)
    except Exception:
        detail = str(exc)
    return JSONResponse(status_code=400, content={"error": "Database integrity error", "detail": detail})


@app.exception_handler(ProgrammingError)
async def sqlalchemy_programming_error_handler(request: Request, exc: ProgrammingError):
    """Return a JSON error for programming/database schema issues (e.g. missing table)."""
    print("[ProgrammingError]", exc, file=sys.stderr)
    try:
        detail = str(exc.orig)
    except Exception:
        detail = str(exc)
    return JSONResponse(status_code=500, content={"error": "Database programming error", "detail": detail})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Fallback handler: always return JSON instead of HTML tracebacks so clients can parse errors."""
    # Print full traceback to server logs
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"error": "Internal Server Error", "detail": str(exc)})


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
