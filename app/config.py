from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

# Obter o diretório raiz do projeto (onde está o .env)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    # JWT - usar valores padrão se não configurado
    jwt_secret_key: str = "default-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 120
    
    # AI/OpenAI
    openai_api_key: str = ""
    
    # App
    app_name: str = "Funny Backend API"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")  # False por padrão em produção
    # reCAPTCHA (Google)
    recaptcha_secret: str | None = None
    recaptcha_site_key: str | None = None
    
    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else ".env"
        env_file_encoding = "utf-8"


settings = Settings()
