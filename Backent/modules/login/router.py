from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from .schemas import LoginRequest, LoginResponse, Token, UserPermission
from .service import LoginService
from utils.standard_responses import api_response_unauthorized, api_response_ok

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login_for_access_token(form_data: LoginRequest, db: Session = Depends(get_db)):
    service = LoginService(db)

    # 1. Autenticar al usuario
    user = service.authenticate_user(email=form_data.email, password=form_data.password)
    if not user:
        return api_response_unauthorized("Correo electrónico o contraseña incorrectos")

    # 2. Obtener permisos
    permissions_list = service.get_user_permissions(user.id_user)

    # 3. Crear el token JWT
    access_token = service.create_jwt_for_user(user, permissions_list)

    # 4. Actualizar último acceso
    service.usuario_service.update_last_access(db, user.id_user)

    # 5. Construir la respuesta
    token_response = Token(access_token=access_token, token_type="bearer")
    permissions_response = [UserPermission(modulo=p["modulo"], accion=p["accion"]) for p in permissions_list]

    login_data = LoginResponse(
        token=token_response,
        permisos=permissions_response
    )

    return api_response_ok(login_data)

