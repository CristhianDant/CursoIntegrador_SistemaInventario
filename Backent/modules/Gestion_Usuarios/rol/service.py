from sqlalchemy.orm import Session
from typing import List, Optional

from .repository import RolRepository
from .schemas import Rol, RolCreate, RolUpdate
from .service_interface import RolServiceInterface

class RolService(RolServiceInterface):
    def __init__(self):
        self.repository = RolRepository()

    def get_all(self, db: Session) -> List[Rol]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, rol_id: int) -> Optional[Rol]:
        return self.repository.get_by_id(db, rol_id)

    def create(self, db: Session, rol: RolCreate) -> Rol:
        return self.repository.create(db, rol)

    def update(self, db: Session, rol_id: int, rol_update: RolUpdate) -> Optional[Rol]:
        return self.repository.update(db, rol_id, rol_update)

    def delete(self, db: Session, rol_id: int) -> bool:
        return self.repository.delete(db, rol_id)

