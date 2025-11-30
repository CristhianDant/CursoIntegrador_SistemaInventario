from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from modules.gestion_almacen_productos.movimiento_productos_terminados.schemas import MovimientoProductoTerminado, MovimientoProductoTerminadoCreate

class MovimientoProductoTerminadoServiceInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[MovimientoProductoTerminado]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, movimiento_id: int) -> MovimientoProductoTerminado:
        pass

    @abstractmethod
    def create(self, db: Session, movimiento: MovimientoProductoTerminadoCreate) -> MovimientoProductoTerminado:
        pass

