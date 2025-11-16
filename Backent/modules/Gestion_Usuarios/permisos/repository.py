from sqlalchemy.orm import Session
from typing import List, Optional

from .model import Permiso
from .schemas import PermisoCreate, PermisoUpdate
from .repository_interface import PermisoRepositoryInterfaz

class PermisoRepository(PermisoRepositoryInterfaz):
    def get_all(self, db: Session) -> List[Permiso]:
        return db.query(Permiso).all()

    def get_by_id(self, db: Session, permiso_id: int) -> Optional[Permiso]:
        return db.query(Permiso).filter(Permiso.id_permiso == permiso_id).first()

    def create(self, db: Session, permiso: PermisoCreate) -> Permiso:
        db_permiso = Permiso(**permiso.model_dump())
        db.add(db_permiso)
        db.commit()
        db.refresh(db_permiso)
        return db_permiso

    def update(self, db: Session, permiso_id: int, permiso_update: PermisoUpdate) -> Optional[Permiso]:
        db_permiso = self.get_by_id(db, permiso_id)
        if db_permiso:
            update_data = permiso_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_permiso, key, value)
            db.commit()
            db.refresh(db_permiso)
        return db_permiso


