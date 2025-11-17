from sqlalchemy.orm import Session
from typing import List, Optional


from .repository import RolRepository
from .schemas import Rol, RolCreate, RolUpdate
from .service_interface import RolServiceInterface
from modules.Gestion_Usuarios.permisos.repository import PermisoRepository

class RolService(RolServiceInterface):
    def __init__(self):
        self.repository = RolRepository()
        self.permiso_repository = PermisoRepository()

    def get_all(self, db: Session) -> List[Rol]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, rol_id: int) -> Optional[Rol]:
        return self.repository.get_by_id(db, rol_id)

    def create(self, db: Session, rol: RolCreate) -> Rol:
        # 1. Validar que todos los permisos existan
        if rol.lista_permisos:
            for permiso_id in rol.lista_permisos:
                permiso = self.permiso_repository.get_by_id(db, permiso_id)
                if not permiso:
                    raise ValueError(f"El permiso con ID {permiso_id} no existe.")


        # 2. Crear el rol
        db_rol = self.repository.create_rol(db, rol)

        # 3. Asignar los permisos al rol (sin commit)
        if rol.lista_permisos:
            self.repository.save_permissions_rol(db, db_rol, rol.lista_permisos)

        # 4. Hacer commit de la transacción
        db.commit()
        db.refresh(db_rol)

        return db_rol

    def update(self, db: Session, rol_id: int, rol_update: RolUpdate) -> Optional[Rol]:
# ... (código existente) ...
        return self.repository.update(db, rol_id, rol_update)

    def delete(self, db: Session, rol_id: int) -> bool:
        return self.repository.delete(db, rol_id)
