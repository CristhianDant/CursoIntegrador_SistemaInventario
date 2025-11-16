from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, Optional

from .model import Permiso
from .schemas import PermisoCreate, PermisoUpdate

class PermisoRepositoryInterfaz(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[Permiso]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, permiso_id: int) -> Optional[Permiso]:
        pass

    @abstractmethod
    def create(self, db: Session, permiso: PermisoCreate) -> Permiso:
        pass

    @abstractmethod
    def update(self, db: Session, permiso_id: int, permiso_update: PermisoUpdate) -> Optional[Permiso]:
        pass


