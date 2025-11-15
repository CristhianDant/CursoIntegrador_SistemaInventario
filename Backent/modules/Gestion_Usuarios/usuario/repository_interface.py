from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, Optional

from .model import Usuario
from .schemas import UsuarioCreate, UsuarioUpdate

class UsuarioRepositoryInterfaz(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[Usuario]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, user_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def get_by_email(self, db: Session, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def create(self, db: Session, user: UsuarioCreate) -> Usuario:
        pass

    @abstractmethod
    def update(self, db: Session, user_id: int, user_update: UsuarioUpdate) -> Optional[Usuario]:
        pass

    @abstractmethod
    def delete(self, db: Session, user_id: int) -> bool:
        pass

    @abstractmethod
    def update_last_access(self, db: Session, user_id: int) -> Optional[Usuario]:
        pass

