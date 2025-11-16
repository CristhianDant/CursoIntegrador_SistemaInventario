from sqlalchemy.orm import Session
from typing import List, Optional

from .model import Rol
from .schemas import RolCreate, RolUpdate
from .repository_interface import RolRepositoryInterfaz

class RolRepository(RolRepositoryInterfaz):
    def get_all(self, db: Session) -> List[Rol]:
        return db.query(Rol).filter(Rol.anulado == False).all()

    def get_by_id(self, db: Session, rol_id: int) -> Optional[Rol]:
        return db.query(Rol).filter(Rol.id_rol == rol_id, Rol.anulado == False).first()

    def create(self, db: Session, rol: RolCreate) -> Rol:
        db_rol = Rol(**rol.dict())
        db.add(db_rol)
        db.commit()
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

