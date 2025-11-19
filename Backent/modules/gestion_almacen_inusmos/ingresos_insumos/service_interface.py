from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from modules.gestion_almacen_inusmos.ingresos_insumos.schemas import IngresoProducto, IngresoProductoCreate, IngresoProductoUpdate

class IngresoProductoServiceInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[IngresoProducto]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, ingreso_id: int) -> IngresoProducto:
        pass

    @abstractmethod
    def create(self, db: Session, ingreso: IngresoProductoCreate) -> IngresoProducto:
        pass

    @abstractmethod
    def update(self, db: Session, ingreso_id: int, ingreso: IngresoProductoUpdate) -> IngresoProducto:
        pass

    @abstractmethod
    def delete(self, db: Session, ingreso_id: int) -> dict:
        pass

