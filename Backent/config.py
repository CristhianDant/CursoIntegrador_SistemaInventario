from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    POST_USER: str
    POST_PASS: str
    POST_DB: str
    POST_PORT: str
    POST_HOST: str = "localhost"
    SECRET_KEY: str
    ALGORITHM_TOK: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # Configuración de Email (Gmail SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # Configurado en .env
    SMTP_PASSWORD: str = ""  # Configurado en .env

    class Config:
        env_file = ".env"

settings = Settings()