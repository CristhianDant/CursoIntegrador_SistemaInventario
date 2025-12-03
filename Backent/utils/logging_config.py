import logging
import sys
import json
from datetime import datetime
from loguru import logger
from config import settings


class InterceptHandler(logging.Handler):
    """
    Manejador de logging para interceptar los registros estándar de Python
    y redirigirlos a Loguru.
    """
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def get_request_id() -> str:
    """
    Obtiene el request_id del contexto actual.
    Retorna cadena vacía si no hay request activo.
    """
    try:
        from middleware.request_id import request_id_ctx
        return request_id_ctx.get()
    except Exception:
        return ""


def json_formatter(record):
    """
    Formateador JSON estructurado para producción.
    
    Genera logs en formato JSON para fácil parsing por
    sistemas de agregación (ELK, Loki, CloudWatch, etc.)
    """
    log_record = {
        "timestamp": record["time"].strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "level": record["level"].name,
        "message": record["message"],
        "logger": record["name"],
        "function": record["function"],
        "line": record["line"],
        "request_id": get_request_id(),
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
    }
    
    # Agregar extras si existen
    if record["extra"]:
        log_record["extra"] = record["extra"]
    
    # Agregar exception si existe
    if record["exception"]:
        log_record["exception"] = {
            "type": record["exception"].type.__name__ if record["exception"].type else None,
            "value": str(record["exception"].value) if record["exception"].value else None,
            "traceback": record["exception"].traceback
        }
    
    record["extra"]["serialized"] = json.dumps(log_record, default=str)
    return "{extra[serialized]}\n"


def text_formatter_with_request_id(record):
    """
    Formateador de texto que incluye request_id.
    """
    request_id = get_request_id()
    rid_str = f"[{request_id[:8]}] " if request_id else ""
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        f"<cyan>{rid_str}</cyan>"
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>\n"
    )


def setup_logging():
    """
    Configura Loguru para que sea el único manejador de logs en la aplicación.
    
    Soporta dos modos:
    - text: Formato legible para desarrollo (con colores)
    - json: Formato JSON estructurado para producción
    """
    # Eliminar cualquier configuración de logger existente
    logger.remove()
    
    # Determinar formato según configuración
    use_json = settings.LOG_FORMAT == "json"
    log_level = settings.LOG_LEVEL
    
    if use_json:
        # Formato JSON para producción (sin colores)
        logger.add(
            sys.stdout,
            format=json_formatter,
            level=log_level,
            colorize=False,
        )
    else:
        # Formato texto con colores para desarrollo
        logger.add(
            sys.stdout,
            format=text_formatter_with_request_id,
            level=log_level,
            colorize=True,
        )
    
    # Archivo de errores (siempre en formato texto para facilitar debug)
    logger.add(
        "logs/error.log",
        level="ERROR",
        rotation=settings.LOG_FILE_ROTATION,
        retention=settings.LOG_FILE_RETENTION,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True,
    )
    
    # Archivo de aplicación (todos los logs)
    logger.add(
        "logs/app.log",
        level="INFO",
        rotation="1 day",
        retention="7 days",
        format=json_formatter if use_json else "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )
    
    # Archivo de sesiones de usuario
    logger.add(
        "logs/sesiones.log",
        level="INFO",
        rotation="1 day",
        retention="30 days",
        format="{message}",
        filter=lambda record: "session_login" in record["extra"] or "session_failed" in record["extra"],
        serialize=False,
    )
    
    # Archivo de health checks y monitoreo
    logger.add(
        "logs/health.log",
        level="WARNING",
        rotation="1 day",
        retention="14 days",
        format=json_formatter,
        filter=lambda record: "health_check" in record["extra"] or "system_alert" in record["extra"],
    )

    # Interceptar todos los logs estándar de Python
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    
    # Reducir verbosidad de librerías externas
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    logger.info(
        f"Logging configurado: level={log_level}, format={settings.LOG_FORMAT}, "
        f"environment={settings.ENVIRONMENT}"
    )
