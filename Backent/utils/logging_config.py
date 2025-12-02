import logging
import sys
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

def setup_logging():
    """
    Configura Loguru para que sea el único manejador de logs en la aplicación.
    """
    # Eliminar cualquier configuración de logger existente y establecer el nivel.
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    )
    # Añadir un manejador para escribir los logs de error en un archivo.
    logger.add(
        "logs/error.log",
        level="ERROR",
        rotation="10 MB",  # Rotar el archivo cuando alcance los 10 MB.
        retention="10 days",  # Mantener los logs de los últimos 10 días.
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        backtrace=True,  # Mostrar el traceback completo para los errores.
        diagnose=True,  # Añadir información de diagnóstico para depuración.
    )
    
    # Añadir un manejador para logs de sesiones de usuario en formato JSON.
    logger.add(
        "logs/sesiones.log",
        level="INFO",
        rotation="1 day",  # Rotar el archivo diariamente.
        retention="30 days",  # Mantener los logs de los últimos 30 días.
        format="{message}",  # Solo el mensaje para permitir formato JSON.
        filter=lambda record: "session_login" in record["extra"] or "session_failed" in record["extra"],
        serialize=False,  # No serializar automáticamente, lo haremos manualmente.
    )

    # Interceptar todos los logs estándar.
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
