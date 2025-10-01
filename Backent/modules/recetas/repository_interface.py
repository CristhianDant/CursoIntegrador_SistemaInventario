from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from modules.recetas.model import Receta
from modules.recetas.schemas import RecetaCreate, RecetaUpdate

class RecetaRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[Receta]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, receta_id: int) -> Optional[Receta]:
        pass

    @abstractmethod
    def create(self, db: Session, receta: RecetaCreate) -> Receta:
        pass

    @abstractmethod
    def update(self, db: Session, receta_id: int, receta: RecetaUpdate) -> Optional[Receta]:
        pass

    @abstractmethod
    def delete(self, db: Session, receta_id: int) -> bool:
        pass

