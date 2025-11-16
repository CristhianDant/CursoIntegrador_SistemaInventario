from sqlalchemy.orm import Session
from typing import List, Optional

from .repository import PermisoRepository
from .schemas import Permiso, PermisoCreate, PermisoUpdate
from .service_interface import PermisoServiceInterface

class PermisoService(PermisoServiceInterface):
    def __init__(self):
        self.repository = PermisoRepository()

    def get_all(self, db: Session) -> List[Permiso]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, permiso_id: int) -> Optional[Permiso]:
        return self.repository.get_by_id(db, permiso_id)

    def create(self, db: Session, permiso: PermisoCreate) -> Permiso:
        return self.repository.create(db, permiso)

    def update(self, db: Session, permiso_id: int, permiso_update: PermisoUpdate) -> Optional[Permiso]:
        return self.repository.update(db, permiso_id, permiso_update)


