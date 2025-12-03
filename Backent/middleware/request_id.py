"""
Middleware de Request ID para trazabilidad de requests.

Genera un UUID único para cada request y lo propaga en headers y logs.
"""

import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger

# Context variable para almacenar el request_id del request actual
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Obtiene el request ID del contexto actual."""
    return request_id_ctx.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware que genera y propaga X-Request-ID.
    
    - Si el cliente envía X-Request-ID, se usa ese valor
    - Si no, se genera un nuevo UUID
    - El request_id se agrega a los headers de respuesta
    - El request_id se almacena en context variable para uso en logs
    """
    
    HEADER_NAME = "X-Request-ID"
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: RequestResponseEndpoint
    ) -> Response:
        # Obtener o generar request_id
        request_id = request.headers.get(self.HEADER_NAME)
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Almacenar en context variable
        token = request_id_ctx.set(request_id)
        
        try:
            # Procesar request
            response = await call_next(request)
            
            # Agregar header a la respuesta
            response.headers[self.HEADER_NAME] = request_id
            
            return response
        finally:
            # Restaurar context variable
            request_id_ctx.reset(token)
