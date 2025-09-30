from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import List, Optional

from modules.productos_terminados.repository import ProductoTerminadoRepository
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

class ProductoTerminadoService(ProductoTerminadoServiceInterface):
    def __init__(self):
        self.repository = ProductoTerminadoRepository()

    def get_all(self, db: Session) -> List[ProductoTerminado]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, producto_id: int) -> Optional[ProductoTerminado]:
        return self.repository.get_by_id(db, producto_id)

    def create(self, db: Session, producto: ProductoTerminadoCreate) -> ProductoTerminado:
        return self.repository.create(db, producto)

    def update(self, db: Session, producto_id: int, producto_update: ProductoTerminadoUpdate) -> Optional[ProductoTerminado]:
        return self.repository.update(db, producto_id, producto_update)

    def delete(self, db: Session, producto_id: int) -> bool:
        return self.repository.delete(db, producto_id)

