from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, Optional

from .schemas import Permiso, UsuarioPermiso, UsuarioPermisoCreate, UsuarioPermisoUpdate

class PermisosServiceInterface(ABC):

    @abstractmethod
    def get_all_permisos(self, db: Session) -> List[Permiso]:
        pass

    @abstractmethod
    def get_all_usuario_permisos(self, db: Session) -> List[UsuarioPermiso]:
        pass

    @abstractmethod
    def get_usuario_permiso_by_id(self, db: Session, usuario_permiso_id: int) -> Optional[UsuarioPermiso]:
        pass

    @abstractmethod
    def create_usuario_permiso(self, db: Session, usuario_permiso: UsuarioPermisoCreate) -> UsuarioPermiso:
        pass

    @abstractmethod
    def delete_usuario_permiso(self, db: Session, usuario_permiso_id: int) -> bool:
        pass

