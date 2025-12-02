from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import json
from datetime import datetime
from loguru import logger

from database import get_db
from .schemas import LoginRequest, LoginResponse, Token
from .service import LoginService
from utils.standard_responses import api_response_unauthorized, api_response_ok

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login_for_access_token(form_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    service = LoginService(db)
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # 1. Autenticar al usuario (usando UsuarioService)
        user = service.authenticate_user(email=form_data.email, password=form_data.password)

        # 2. Obtener roles
        roles = service.get_user_roles(user)

        # 3. Crear el token JWT
        access_token = service.create_jwt_for_user(user, roles)

        # 4. Actualizar último acceso
        service.usuario_service.update_last_access(db, user.id_user)

        # 5. Registrar inicio de sesión exitoso
        session_log = {
            "event": "login_success",
            "timestamp": datetime.now().isoformat(),
            "user_id": user.id_user,
            "nombre": user.nombre,
            "apellidos": user.apellidos,
            "email": user.email,
            "roles": roles,
            "ip_address": client_ip
        }
        logger.bind(session_login=True).info(json.dumps(session_log, ensure_ascii=False))

        # 6. Construir la respuesta
        token_response = Token(access_token=access_token, token_type="bearer")

        login_data = LoginResponse(
            token=token_response,
            roles=user.roles,
            nombre=user.nombre,
            email=user.email
        )

        return api_response_ok(login_data)
    except ValueError as e:
        error_msg = str(e)
        # Registrar intento de login fallido
        failed_log = {
            "event": "login_failed",
            "timestamp": datetime.now().isoformat(),
            "email": form_data.email,
            "ip_address": client_ip,
            "reason": error_msg
        }
        logger.bind(session_failed=True).warning(json.dumps(failed_log, ensure_ascii=False))
        return api_response_unauthorized(error_msg)
    except Exception as e:
        error_msg = str(e)
        # Registrar error inesperado en login
        error_log = {
            "event": "login_error",
            "timestamp": datetime.now().isoformat(),
            "email": form_data.email,
            "ip_address": client_ip,
            "error": error_msg
        }
        logger.bind(session_failed=True).error(json.dumps(error_log, ensure_ascii=False))
        return api_response_unauthorized("Error al autenticar al usuario")
