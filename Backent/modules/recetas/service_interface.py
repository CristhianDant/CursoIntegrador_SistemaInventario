from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from modules.recetas.schemas import Receta, RecetaCreate, RecetaUpdate

class RecetaServiceInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[Receta]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, receta_id: int) -> Receta:
        pass

    @abstractmethod
    def create(self, db: Session, receta: RecetaCreate) -> Receta:
        pass

    @abstractmethod
    def update(self, db: Session, receta_id: int, receta: RecetaUpdate) -> Receta:
        pass

    @abstractmethod
    def delete(self, db: Session, receta_id: int) -> dict:
        pass
