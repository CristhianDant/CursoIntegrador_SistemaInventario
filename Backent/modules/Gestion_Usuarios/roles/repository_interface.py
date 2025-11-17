from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, Optional

from .model import Rol
from .schemas import RolCreate, RolUpdate

class RolRepositoryInterfaz(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[Rol]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, rol_id: int) -> Optional[Rol]:
        pass

    @abstractmethod
    def create_rol(self, db: Session, rol: RolCreate) -> Rol:
        pass

    @abstractmethod
    def update(self, db: Session, rol_id: int, rol_update: RolUpdate) -> Optional[Rol]:
        pass

    @abstractmethod
    def delete(self, db: Session, rol_id: int) -> bool:
        pass

