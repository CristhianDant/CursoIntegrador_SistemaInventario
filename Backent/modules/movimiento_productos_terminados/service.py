from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from modules.movimiento_productos_terminados.schemas import MovimientoProductoTerminado, MovimientoProductoTerminadoCreate
from modules.movimiento_productos_terminados.repository import MovimientoProductoTerminadoRepository
from modules.movimiento_productos_terminados.service_interface import MovimientoProductoTerminadoServiceInterface

class MovimientoProductoTerminadoService(MovimientoProductoTerminadoServiceInterface):
    def __init__(self):
        self.repository = MovimientoProductoTerminadoRepository()

    def get_all(self, db: Session) -> List[MovimientoProductoTerminado]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, movimiento_id: int) -> MovimientoProductoTerminado:
        movimiento = self.repository.get_by_id(db, movimiento_id)
        if not movimiento:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento de producto terminado no encontrado")
        return movimiento

    def create(self, db: Session, movimiento: MovimientoProductoTerminadoCreate) -> MovimientoProductoTerminado:
        return self.repository.create(db, movimiento)

