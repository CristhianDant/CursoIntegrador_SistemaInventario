"""
Middleware de la aplicación.

Incluye middlewares personalizados para:
- Request ID (trazabilidad)
- Timing (métricas de rendimiento)
"""

from .request_id import RequestIDMiddleware, get_request_id, request_id_ctx

__all__ = [
    "RequestIDMiddleware",
    "get_request_id",
    "request_id_ctx"
]
