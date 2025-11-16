from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, Optional

from .schemas import Rol, RolCreate, RolUpdate

class RolServiceInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[Rol]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, rol_id: int) -> Optional[Rol]:
        pass

    @abstractmethod
    def create(self, db: Session, rol: RolCreate) -> Rol:
        pass

    @abstractmethod
    def update(self, db: Session, rol_id: int, rol_update: RolUpdate) -> Optional[Rol]:
        pass

    @abstractmethod
    def delete(self, db: Session, rol_id: int) -> bool:
        pass

