from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from .schemas import LoginRequest, LoginResponse, Token
from .service import LoginService
from utils.standard_responses import api_response_unauthorized, api_response_ok

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login_for_access_token(form_data: LoginRequest, db: Session = Depends(get_db)):
    service = LoginService(db)

    # 1. Autenticar al usuario (ahora carga roles y permisos)
    user = service.authenticate_user(email=form_data.email, password=form_data.password)
    if not user:
        return api_response_unauthorized("Correo electrónico o contraseña incorrectos")

    # 2. Obtener roles y permisos
    roles, permissions = service.get_user_roles_and_permissions(user)

    # 3. Crear el token JWT
    access_token = service.create_jwt_for_user(user, roles, permissions)

    # 4. Actualizar último acceso
    service.usuario_service.update_last_access(db, user.id_user)

    # 5. Construir la respuesta
    token_response = Token(access_token=access_token, token_type="bearer")

    login_data = LoginResponse(
        token=token_response,
        roles=user.roles,
        nombre=user.nombre,
        email=user.email
    )

    return api_response_ok(login_data)
