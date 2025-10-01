from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from modules.calidad_desperdicio_merma.model import CalidadDesperdicioMerma
from modules.calidad_desperdicio_merma.schemas import MermaCreate, MermaUpdate

class MermaRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[CalidadDesperdicioMerma]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, merma_id: int) -> Optional[CalidadDesperdicioMerma]:
        pass

    @abstractmethod
    def create(self, db: Session, merma: MermaCreate) -> CalidadDesperdicioMerma:
        pass

    @abstractmethod
    def update(self, db: Session, merma_id: int, merma: MermaUpdate) -> Optional[CalidadDesperdicioMerma]:
        pass

    @abstractmethod
    def delete(self, db: Session, merma_id: int) -> bool:
        pass

