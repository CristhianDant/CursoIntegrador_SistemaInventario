from sqlalchemy.orm import Session
from typing import List, Optional

from .model import Rol
from .schemas import RolCreate, RolUpdate
from .repository_interface import RolRepositoryInterfaz
from modules.Gestion_Usuarios.permisos.model import Permiso

class RolRepository(RolRepositoryInterfaz):
    def get_all(self, db: Session) -> List[Rol]:
        return db.query(Rol).filter(Rol.anulado == False).all()

    def get_by_id(self, db: Session, rol_id: int) -> Optional[Rol]:
        return db.query(Rol).filter(Rol.id_rol == rol_id, Rol.anulado == False).first()

    from modules.Gestion_Usuarios.permisos.model import Permiso

# ... (código existente) ...

    def create_rol(self, db: Session, rol: RolCreate) -> Rol:
        """
        Crea un nuevo objeto Rol en la base de datos sin asociar permisos.
        No hace commit de la transacción.
        """
        rol_data = rol.model_dump(exclude={'lista_permisos'})
        db_rol = Rol(**rol_data)
        db.add(db_rol)
        db.flush()  # Asegura que el objeto tenga un ID antes de salir
        db.refresh(db_rol)
        return db_rol

    def update(self, db: Session, rol_id: int, rol_update: RolUpdate) -> Optional[Rol]:
        db_rol = self.get_by_id(db, rol_id)
        if db_rol:
            update_data = rol_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_rol, key, value)
            db.commit()
            db.refresh(db_rol)
        return db_rol

    def delete(self, db: Session, rol_id: int) -> bool:
        db_rol = self.get_by_id(db, rol_id)
        if db_rol:
            db_rol.anulado = True
            db.commit()
            return True
        return False



    def save_permissions_rol(self, db: Session, db_rol: Rol, permisos_ids: List[int]):
        """
        Asocia una lista de permisos a un objeto Rol ya existente en la sesión.
        No hace commit de la transacción.
        """
        if permisos_ids:
            permisos = db.query(Permiso).filter(Permiso.id_permiso.in_(permisos_ids)).all()
            db_rol.permisos = permisos
            db.flush()


