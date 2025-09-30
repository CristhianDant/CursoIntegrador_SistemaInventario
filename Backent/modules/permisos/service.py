from sqlalchemy.orm import Session
from typing import List, Optional

from .repository import PermisosRepository
from .schemas import Permiso, UsuarioPermiso, UsuarioPermisoCreate, UsuarioPermisoUpdate
from .service_interface import PermisosServiceInterface

class PermisosService(PermisosServiceInterface):

    def __init__(self):
        self.repository = PermisosRepository()

    def get_all_permisos(self, db: Session) -> List[Permiso]:
        return self.repository.get_all_permisos(db)

    def get_all_usuario_permisos(self, db: Session) -> List[UsuarioPermiso]:
        return self.repository.get_all_usuario_permisos(db)

    def get_usuario_permiso_by_id(self, db: Session, usuario_permiso_id: int) -> Optional[UsuarioPermiso]:
        return self.repository.get_usuario_permiso_by_id(db, usuario_permiso_id)

    def create_usuario_permiso(self, db: Session, usuario_permiso: UsuarioPermisoCreate) -> UsuarioPermiso:
        return self.repository.create_usuario_permiso(db, usuario_permiso)

    def delete_usuario_permiso(self, db: Session, usuario_permiso_id: int) -> bool:
        usuario_permiso_update = UsuarioPermisoUpdate(anulado=True)
        updated_permiso = self.repository.update_usuario_permiso(db, usuario_permiso_id, usuario_permiso_update)
        return updated_permiso is not None

