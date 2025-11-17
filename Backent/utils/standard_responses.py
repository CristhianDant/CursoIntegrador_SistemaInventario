from typing import Any
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from loguru import logger

# --- Funciones de Respuesta Estándar ---

def api_response_ok(data: Any) -> JSONResponse:
    """
    Genera una respuesta HTTP 200 (OK) estandarizada.

    Args:
        data (Any): Los datos a incluir en la respuesta.

    Returns:
        JSONResponse: Una respuesta JSON con código 200.
    """
    response_body = {"data": data, "success": True, "code": 200}
    return JSONResponse(status_code=200, content=jsonable_encoder(response_body))

def api_response_bad_request(error_message) -> JSONResponse:
    """
    Genera una respuesta HTTP 400 (Bad Request) estandarizada y registra el error.

    Args:
        error_message (str): El mensaje de error a incluir en la respuesta.

    Returns:
        JSONResponse: Una respuesta JSON con código 400.
    """
    response_body = {"data": error_message, "success": False, "code": 400}
    logger.opt(depth=1).warning(f"Error 400: {error_message}")
    return JSONResponse(status_code=400, content=jsonable_encoder(response_body))

def api_response_internal_server_error(error_message: str) -> JSONResponse:
    """
    Genera una respuesta HTTP 500 (Internal Server Error) estandarizada y registra el error.

    Args:
        error_message (str): El mensaje de error a incluir en la respuesta.

    Returns:
        JSONResponse: Una respuesta JSON con código 500.
    """
    response_body = {"data": error_message, "success": False, "code": 500}
    logger.opt(depth=1, exception=True).error(f"Error 500: {error_message}")
    return JSONResponse(status_code=500, content=jsonable_encoder(response_body))

def api_response_not_found(error_message: str) -> JSONResponse:
    """
    Genera una respuesta HTTP 404 (Not Found) estandarizada y registra el error.

    Args:
        error_message (str): El mensaje de error a incluir en la respuesta.

    Returns:
        JSONResponse: Una respuesta JSON con código 404.
    """
    response_body = {"data": error_message, "success": False, "code": 404}
    logger.opt(depth=1).warning(f"Error 404: {error_message}")
    return JSONResponse(status_code=404, content=jsonable_encoder(response_body))

def api_response_unauthorized(error_message: str) -> JSONResponse:
    """
    Genera una respuesta HTTP 401 (Unauthorized) estandarizada y registra el error.

    Args:
        error_message (str): El mensaje de error a incluir en la respuesta.

    Returns:
        JSONResponse: Una respuesta JSON con código 401.
    """
    response_body = {"data": error_message, "success": False, "code": 401}
    logger.opt(depth=1).warning(f"Error 401: {error_message}")
    return JSONResponse(status_code=401, content=jsonable_encoder(response_body))
