from sqlalchemy.orm import Session
from typing import List, Optional

from .model import Permiso, UsuarioPermiso
from .schemas import UsuarioPermisoCreate, UsuarioPermisoUpdate
from .repository_interface import PermisosRepositoryInterfaz

class PermisosRepository(PermisosRepositoryInterfaz):

    def get_all_permisos(self, db: Session) -> List[Permiso]:
        return db.query(Permiso).all()

    def get_all_usuario_permisos(self, db: Session) -> List[UsuarioPermiso]:
        return db.query(UsuarioPermiso).filter(UsuarioPermiso.anulado == False).all()

    def get_usuario_permiso_by_id(self, db: Session, usuario_permiso_id: int) -> Optional[UsuarioPermiso]:
        return db.query(UsuarioPermiso).filter(UsuarioPermiso.id_user_permiso == usuario_permiso_id, UsuarioPermiso.anulado == False).first()

    def create_usuario_permiso(self, db: Session, usuario_permiso: UsuarioPermisoCreate) -> UsuarioPermiso:
        db_usuario_permiso = UsuarioPermiso(**usuario_permiso.model_dump())
        db.add(db_usuario_permiso)
        db.commit()
        db.refresh(db_usuario_permiso)
        return db_usuario_permiso

    def update_usuario_permiso(self, db: Session, usuario_permiso_id: int, usuario_permiso_update: UsuarioPermisoUpdate) -> Optional[UsuarioPermiso]:
        # Realiza la actualización en una sola consulta para mayor eficiencia
        rows_affected = db.query(UsuarioPermiso).filter(
            UsuarioPermiso.id_user_permiso == usuario_permiso_id,
            UsuarioPermiso.anulado == False
        ).update({"anulado": usuario_permiso_update.anulado})

        if rows_affected > 0:
            db.commit()
            # Después de una actualización exitosa, obtenemos el objeto actualizado para devolverlo
            return self.get_usuario_permiso_by_id(db, usuario_permiso_id)

        return None
