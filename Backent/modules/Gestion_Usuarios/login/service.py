from sqlalchemy.orm import Session
from typing import List

from modules.Gestion_Usuarios.usuario.model import Usuario
from modules.Gestion_Usuarios.permisos.model import Permiso #UsuarioPermiso
from security.password_utils import verify_password
from security.jwt_utils import create_access_token
from modules.Gestion_Usuarios.usuario.service import UsuarioService

class LoginService:

    def __init__(self, db: Session):
        self.db = db
        self.usuario_service = UsuarioService()

    def authenticate_user(self, email: str, password: str) -> Usuario | None:
        """
        Autentica a un usuario.
        - Busca al usuario por email.
        - Verifica que no esté anulado.
        - Compara la contraseña.
        """
        user = self.usuario_service.get_by_email(self.db, email)
        if not user or user.anulado:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def get_user_permissions(self, user_id: int) -> List[dict]:
        """
        Obtiene los permisos de un usuario en formato de diccionario.
        """
        permisos_query = self.db.query(
            Permiso.modulo,
            Permiso.accion
        ).join(
            UsuarioPermiso, UsuarioPermiso.id_permiso == Permiso.id_permiso
        ).filter(
            UsuarioPermiso.id_user == user_id,
            UsuarioPermiso.anulado == False
        ).all()

        return [{"modulo": modulo, "accion": accion} for modulo, accion in permisos_query]

    def create_jwt_for_user(self, user: Usuario, permissions: List[dict]) -> str:
        """
        Crea un token JWT para un usuario, incluyendo sus permisos.
        """
        token_data = {
            "sub": user.email,
            "nombre": user.nombre,
            "es_admin": user.es_admin,
            "permisos": permissions
        }
        access_token = create_access_token(data=token_data)
        return access_token

