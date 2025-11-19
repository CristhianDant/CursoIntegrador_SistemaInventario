from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from modules.gestion_almacen_inusmos.movimiento_insumos.schemas import MovimientoInsumo, MovimientoInsumoCreate

class MovimientoInsumoServiceInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[MovimientoInsumo]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, movimiento_id: int) -> MovimientoInsumo:
        pass

    @abstractmethod
    def create(self, db: Session, movimiento: MovimientoInsumoCreate) -> MovimientoInsumo:
        pass

