from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# URL do banco vinda do config.py
DATABASE_URL = settings.DATABASE_URL

# Cria engine de conexão
engine = create_engine(DATABASE_URL)

# Cria sessão para interagir com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os models (ex.: Usuario, Atividade etc.)
Base = declarative_base()


# Dependência do FastAPI para injetar sessão no endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
