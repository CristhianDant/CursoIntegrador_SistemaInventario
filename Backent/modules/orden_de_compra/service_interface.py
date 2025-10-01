from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from modules.orden_de_compra.schemas import OrdenDeCompra, OrdenDeCompraCreate, OrdenDeCompraUpdate

class OrdenDeCompraServiceInterface(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> List[OrdenDeCompra]:
        pass

    @abstractmethod
    def get_by_id(self, db: Session, orden_id: int) -> OrdenDeCompra:
        pass

    @abstractmethod
    def create(self, db: Session, orden: OrdenDeCompraCreate) -> OrdenDeCompra:
        pass

    @abstractmethod
    def update(self, db: Session, orden_id: int, orden: OrdenDeCompraUpdate) -> OrdenDeCompra:
        pass

    @abstractmethod
    def delete(self, db: Session, orden_id: int) -> dict:
        pass

