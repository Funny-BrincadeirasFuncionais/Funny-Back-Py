from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    db_name: str
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 120
    
    # App
    app_name: str = "Funny Backend API"
    app_version: str = "1.0.0"
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()
