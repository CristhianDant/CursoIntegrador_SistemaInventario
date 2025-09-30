from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, Optional

from modules.productos_terminados.schemas import ProductoTerminado, ProductoTerminadoCreate, ProductoTerminadoUpdate

class ProductoTerminadoServiceInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[ProductoTerminado]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, producto_id: int) -> Optional[ProductoTerminado]:
        pass

    @abstractmethod
    def create(self, db: Session, producto: ProductoTerminadoCreate) -> ProductoTerminado:
        pass

    @abstractmethod
    def update(self, db: Session, producto_id: int, producto_update: ProductoTerminadoUpdate) -> Optional[ProductoTerminado]:
        pass

    @abstractmethod
    def delete(self, db: Session, producto_id: int) -> bool:
        pass

