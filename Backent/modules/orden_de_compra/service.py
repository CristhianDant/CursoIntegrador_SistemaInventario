from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from modules.orden_de_compra.schemas import OrdenDeCompra, OrdenDeCompraCreate, OrdenDeCompraUpdate
from modules.orden_de_compra.repository import OrdenDeCompraRepository
from modules.orden_de_compra.service_interface import OrdenDeCompraServiceInterface

class OrdenDeCompraService(OrdenDeCompraServiceInterface):
    def __init__(self):
        self.repository = OrdenDeCompraRepository()

    def get_all(self, db: Session, activas_solo: bool = True) -> List[OrdenDeCompra]:
        return self.repository.get_all(db, activas_solo=activas_solo)

    def get_by_id(self, db: Session, orden_id: int) -> OrdenDeCompra:
        orden = self.repository.get_by_id(db, orden_id)
        if not orden:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        return orden

    def create(self, db: Session, orden: OrdenDeCompraCreate) -> OrdenDeCompra:
        return self.repository.create(db, orden)

    def update(self, db: Session, orden_id: int, orden: OrdenDeCompraUpdate) -> OrdenDeCompra:
        orden_actualizada = self.repository.update(db, orden_id, orden)
        if not orden_actualizada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        return orden_actualizada

    def delete(self, db: Session, orden_id: int) -> dict:
        if not self.repository.delete(db, orden_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        return {"message": "Orden de compra anulada correctamente"}

