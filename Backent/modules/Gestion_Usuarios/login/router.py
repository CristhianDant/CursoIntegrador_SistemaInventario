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
    try:
        # 1. Autenticar al usuario (usando UsuarioService)
        user = service.authenticate_user(email=form_data.email, password=form_data.password)

        # 2. Obtener roles
        roles = service.get_user_roles(user)

        # 3. Crear el token JWT
        access_token = service.create_jwt_for_user(user, roles)

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
    except ValueError as e:
        return api_response_unauthorized(str(e))
    except Exception as e:
        return api_response_unauthorized("Error al autenticar al usuario")
