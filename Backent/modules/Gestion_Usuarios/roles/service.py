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
        # 1. Buscar el rol existente
        db_rol = self.repository.get_by_id(db, rol_id)
        if not db_rol:
            raise ValueError("El rol no existe.")

        # 2. Validar permisos si se proporcionan en la actualización
        if rol_update.lista_permisos is not None:
            for permiso_id in rol_update.lista_permisos:
                permiso = self.permiso_repository.get_by_id(db, permiso_id)
                if not permiso:
                    db.rollback()
                    raise ValueError(f"El permiso con ID {permiso_id} no existe.")

        # 3. Actualizar los campos básicos del rol
        self.repository.update(db, db_rol, rol_update)

        # 4. Si se proporcionó una lista de permisos, limpiar los antiguos y guardar los nuevos
        if rol_update.lista_permisos is not None:
            self.repository.clear_permissions_from_rol(db, db_rol)
            if rol_update.lista_permisos:
                self.repository.save_permissions_rol(db, db_rol, rol_update.lista_permisos)

        # 5. Hacer commit de la transacción
        db.commit()
        db.refresh(db_rol)

        return db_rol

    def delete(self, db: Session, rol_id: int) -> bool:
        return self.repository.delete(db, rol_id)
