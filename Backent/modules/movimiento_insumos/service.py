from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from modules.movimiento_insumos.schemas import MovimientoInsumo, MovimientoInsumoCreate
from modules.movimiento_insumos.repository import MovimientoInsumoRepository
from modules.movimiento_insumos.service_interface import MovimientoInsumoServiceInterface

class MovimientoInsumoService(MovimientoInsumoServiceInterface):
    def __init__(self):
        self.repository = MovimientoInsumoRepository()

    def get_all(self, db: Session) -> List[MovimientoInsumo]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, movimiento_id: int) -> MovimientoInsumo:
        movimiento = self.repository.get_by_id(db, movimiento_id)
        if not movimiento:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movimiento de insumo no encontrado")
        return movimiento

    def create(self, db: Session, movimiento: MovimientoInsumoCreate) -> MovimientoInsumo:
        return self.repository.create(db, movimiento)

