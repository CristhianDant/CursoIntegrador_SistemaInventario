from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    POST_USER: str
    POST_PASS: str
    POST_DB: str
    POST_PORT: str
    SECRET_KEY: str
    ALGORITHM_TOK: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    HOST_DB: str

    # Configuración de Email (Gmail SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""  # Configurado en .env
    SMTP_PASSWORD: str = ""  # Configurado en .env

    # ==================== SCHEDULER ====================
    SCHEDULER_ENABLED: bool = True
    SCHEDULER_HORA_DEFAULT: int = 6  # Hora para ejecutar jobs diarios (6 AM)
    SCHEDULER_MINUTO_DEFAULT: int = 0
    SCHEDULER_TIMEZONE: str = "America/Lima"

    # ==================== LOGGING ====================
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["text", "json"] = "text"  # json para producción
    LOG_FILE_ROTATION: str = "10 MB"
    LOG_FILE_RETENTION: str = "10 days"

    # ==================== MONITOREO ====================
    ENABLE_METRICS: bool = True  # Habilitar Prometheus metrics
    METRICS_PATH: str = "/metrics"
    
    # Umbrales de health checks
    DB_RESPONSE_TIME_WARNING_MS: int = 100  # Amarillo si > 100ms
    DB_RESPONSE_TIME_CRITICAL_MS: int = 500  # Rojo si > 500ms
    
    # Alertas de salud del sistema
    HEALTH_CHECK_ALERT_ENABLED: bool = True
    HEALTH_CHECK_INTERVAL_SECONDS: int = 60

    # ==================== ENVIRONMENT ====================
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    APP_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"


settings = Settings()