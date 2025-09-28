import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configurações da aplicação.
    Carrega variáveis de ambiente automaticamente.
    """

    # Banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    # Se não houver DATABASE_URL, usa SQLite local para testes

    # JWT e outros
    JWT_SECRET: str = os.getenv("JWT_SECRET", "changeme")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    class Config:
        env_file = ".env"  # permite usar variáveis de um arquivo .env local


# Instância global para usar em toda a aplicação
settings = Settings()
