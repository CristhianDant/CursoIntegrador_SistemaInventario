from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from modules.movimiento_insumos.model import MovimientoInsumo
from modules.movimiento_insumos.schemas import MovimientoInsumoCreate

class MovimientoInsumoRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[MovimientoInsumo]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, movimiento_id: int) -> Optional[MovimientoInsumo]:
        pass

    @abstractmethod
    def create(self, db: Session, movimiento: MovimientoInsumoCreate) -> MovimientoInsumo:
        pass

