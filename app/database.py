from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# Pega a URL do banco do config.py
DATABASE_URL = settings.DATABASE_URL

# Cria engine de conexão
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Cria sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os models herdarem
Base = declarative_base()


# Dependency para usar nos endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
