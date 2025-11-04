from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Usar variável de ambiente DATABASE_URL (PostgreSQL no Render)
# Fallback para SQLite apenas para desenvolvimento local
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./funny.db")

# Render usa postgres://, mas SQLAlchemy 1.4+ precisa de postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Criar engine com configurações apropriadas para cada banco
if DATABASE_URL.startswith("postgresql://"):
    # PostgreSQL - sem check_same_thread
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verifica conexão antes de usar
        pool_size=5,         # Número de conexões no pool
        max_overflow=10      # Conexões extras se necessário
    )
else:
    # SQLite - apenas para desenvolvimento local
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Criar SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
