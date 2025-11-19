from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProducto
from modules.gestion_almacen_inusmos.ingresos_insumos.schemas import IngresoProductoCreate, IngresoProductoUpdate

class IngresoProductoRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[IngresoProducto]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, ingreso_id: int) -> Optional[IngresoProducto]:
        pass

    @abstractmethod
    def create(self, db: Session, ingreso: IngresoProductoCreate) -> IngresoProducto:
        pass

    @abstractmethod
    def update(self, db: Session, ingreso_id: int, ingreso: IngresoProductoUpdate) -> Optional[IngresoProducto]:
        pass

    @abstractmethod
    def delete(self, db: Session, ingreso_id: int) -> bool:
        pass

