from sqlalchemy.orm import Session, joinedload
from typing import List, Set, Tuple

from modules.Gestion_Usuarios.usuario.model import Usuario
from modules.Gestion_Usuarios.roles.model import Rol
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
        - Carga anticipadamente los roles y permisos.
        """
        user = self.db.query(Usuario).options(
            joinedload(Usuario.roles)
        ).filter(Usuario.email == email).first()

        if not user or user.anulado:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def get_user_roles_and_permissions(self, user: Usuario) -> Tuple[List[str], Set[str]]:
        """
        Obtiene los nombres de los roles y un conjunto de permisos únicos para un usuario.
        """
        role_names = [rol.nombre_rol for rol in user.roles]
        permissions = set()
        for rol in user.roles:
            for permiso in rol.permisos:
                permissions.add(f"{permiso.modulo.value}:{permiso.accion}")
        return role_names, permissions

    def create_jwt_for_user(self, user: Usuario, roles: List[str], permissions: Set[str]) -> str:
        """
        Crea un token JWT para un usuario, incluyendo sus roles y permisos.
        """
        token_data = {
            "sub": user.email,
            "nombre": user.nombre,
            "roles": roles,
            "permisos": list(permissions)
        }
        access_token = create_access_token(data=token_data)
        return access_token
