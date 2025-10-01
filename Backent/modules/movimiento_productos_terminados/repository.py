from typing import List, Optional
from sqlalchemy.orm import Session
from modules.movimiento_productos_terminados.model import MovimientoProductoTerminado
from modules.movimiento_productos_terminados.schemas import MovimientoProductoTerminadoCreate
from modules.movimiento_productos_terminados.repository_interface import MovimientoProductoTerminadoRepositoryInterface

class MovimientoProductoTerminadoRepository(MovimientoProductoTerminadoRepositoryInterface):
    def get_all(self, db: Session) -> List[MovimientoProductoTerminado]:
        return db.query(MovimientoProductoTerminado).filter(MovimientoProductoTerminado.anulado == False).all()

    def get_by_id(self, db: Session, movimiento_id: int) -> Optional[MovimientoProductoTerminado]:
        return db.query(MovimientoProductoTerminado).filter(MovimientoProductoTerminado.id_movimiento == movimiento_id, MovimientoProductoTerminado.anulado == False).first()

    def create(self, db: Session, movimiento: MovimientoProductoTerminadoCreate) -> MovimientoProductoTerminado:
        db_movimiento = MovimientoProductoTerminado(**movimiento.model_dump())
        db.add(db_movimiento)
        db.commit()
        db.refresh(db_movimiento)
        return db_movimiento

