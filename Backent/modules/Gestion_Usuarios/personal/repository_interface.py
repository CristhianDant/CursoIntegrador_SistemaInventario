from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Optional

from .model import Personal
from .schemas import PersonalCreate, PersonalUpdate


class PersonalRepositoryInterface(ABC):
    @abstractmethod
    def get_by_id(self, db: Session, personal_id: int) -> Optional[Personal]:
        pass

    @abstractmethod
    def get_by_usuario_id(self, db: Session, usuario_id: int) -> Optional[Personal]:
        pass

    @abstractmethod
    def get_by_dni(self, db: Session, dni: str) -> Optional[Personal]:
        pass

    @abstractmethod
    def create(self, db: Session, personal_data: dict) -> Personal:
        pass

    @abstractmethod
    def update(self, db: Session, personal_id: int, personal_update: PersonalUpdate) -> Optional[Personal]:
        pass

    @abstractmethod
    def update_estado(self, db: Session, personal_id: int, anulado: bool) -> Optional[Personal]:
        pass
