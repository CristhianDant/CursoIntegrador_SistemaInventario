from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from modules.gestion_almacen_inusmos.ingresos_insumos.schemas import IngresoProducto, IngresoProductoCreate, IngresoProductoUpdate
from modules.gestion_almacen_inusmos.ingresos_insumos.repository import IngresoProductoRepository
from modules.gestion_almacen_inusmos.ingresos_insumos.service_interface import IngresoProductoServiceInterface

class IngresoProductoService(IngresoProductoServiceInterface):
    def __init__(self):
        self.repository = IngresoProductoRepository()

    def get_all(self, db: Session) -> List[IngresoProducto]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, ingreso_id: int) -> IngresoProducto:
        ingreso = self.repository.get_by_id(db, ingreso_id)
        if not ingreso:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingreso de producto no encontrado")
        return ingreso

    def create(self, db: Session, ingreso: IngresoProductoCreate) -> IngresoProducto:
        return self.repository.create(db, ingreso)

    def update(self, db: Session, ingreso_id: int, ingreso: IngresoProductoUpdate) -> IngresoProducto:
        ingreso_actualizado = self.repository.update(db, ingreso_id, ingreso)
        if not ingreso_actualizado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingreso de producto no encontrado")
        return ingreso_actualizado

    def delete(self, db: Session, ingreso_id: int) -> dict:
        if not self.repository.delete(db, ingreso_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingreso de producto no encontrado")
        return {"message": "Ingreso de producto anulado correctamente"}

