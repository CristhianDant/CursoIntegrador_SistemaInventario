from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, Optional

from .model import Rol, UsuarioRol, RolPermiso
from .schemas import RolCreate, RolUpdate, UsuarioRolCreate, RolPermisoCreate

class RolRepositoryInterfaz(ABC):
    # Métodos para Rol
    @abstractmethod
    def get_all_roles(self, db: Session) -> List[Rol]:
        pass

    @abstractmethod
    def get_rol_by_id(self, db: Session, rol_id: int) -> Optional[Rol]:
        pass

    @abstractmethod
    def create_rol(self, db: Session, rol: RolCreate) -> Rol:
        pass

    @abstractmethod
    def update_rol(self, db: Session, rol_id: int, rol_update: RolUpdate) -> Optional[Rol]:
        pass

    # Métodos para UsuarioRol
    @abstractmethod
    def assign_rol_to_user(self, db: Session, usuario_rol: UsuarioRolCreate) -> UsuarioRol:
        pass

    @abstractmethod
    def get_user_roles(self, db: Session, user_id: int) -> List[Rol]:
        pass

    # Métodos para RolPermiso
    @abstractmethod
    def assign_permission_to_rol(self, db: Session, rol_permiso: RolPermisoCreate) -> RolPermiso:
        pass

    @abstractmethod
    def get_rol_permissions(self, db: Session, rol_id: int) -> List[RolPermiso]:
        pass

