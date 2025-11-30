from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from modules.gestion_almacen_productos.movimiento_productos_terminados.model import MovimientoProductoTerminado
from modules.gestion_almacen_productos.movimiento_productos_terminados.schemas import MovimientoProductoTerminadoCreate

class MovimientoProductoTerminadoRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[MovimientoProductoTerminado]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, movimiento_id: int) -> Optional[MovimientoProductoTerminado]:
        pass

    @abstractmethod
    def create(self, db: Session, movimiento: MovimientoProductoTerminadoCreate) -> MovimientoProductoTerminado:
        pass

