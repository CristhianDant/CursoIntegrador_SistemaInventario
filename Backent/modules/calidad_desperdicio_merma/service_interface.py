from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from modules.calidad_desperdicio_merma.schemas import Merma, MermaCreate, MermaUpdate

class MermaServiceInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[Merma]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, merma_id: int) -> Merma:
        pass

    @abstractmethod
    def create(self, db: Session, merma: MermaCreate) -> Merma:
        pass

    @abstractmethod
    def update(self, db: Session, merma_id: int, merma: MermaUpdate) -> Merma:
        pass

    @abstractmethod
    def delete(self, db: Session, merma_id: int) -> dict:
        pass

