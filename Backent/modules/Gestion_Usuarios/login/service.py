from sqlalchemy.orm import Session
from typing import List

from modules.Gestion_Usuarios.usuario.model import Usuario
from modules.Gestion_Usuarios.usuario.service import UsuarioService
from security.password_utils import verify_password
from security.jwt_utils import create_access_token


class LoginService:

    def __init__(self, db: Session):
        self.db = db
        self.usuario_service = UsuarioService()

    def authenticate_user(self, email: str, password: str) -> Usuario | None:
        """
        Autentica a un usuario usando el UsuarioService.
        - Busca al usuario por email (carga los roles automáticamente).
        - Verifica que no esté anulado.
        - Compara la contraseña.
        """
        user = self.usuario_service.get_by_email(self.db, email)

        if not user :
            return ValueError("El usuario no existe.")
        if user.anulado:
            return ValueError("El usuario está anulado.")

        if not verify_password(password, user.password):
            return None
        return user

    def get_user_roles(self, user: Usuario) -> List[str]:
        """
        Obtiene los nombres de los roles para un usuario.
        """
        return [rol.nombre_rol for rol in user.roles]

    def create_jwt_for_user(self, user: Usuario, roles: List[str]) -> str:
        """
        Crea un token JWT para un usuario, incluyendo sus roles.
        """
        token_data = {
            "sub": user.email,
            "nombre": user.nombre,
            "roles": roles
        }
        access_token = create_access_token(data=token_data)
        return access_token
