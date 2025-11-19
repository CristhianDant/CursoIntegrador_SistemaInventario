from typing import List, Optional
from sqlalchemy.orm import Session
from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
from modules.gestion_almacen_inusmos.movimiento_insumos.schemas import MovimientoInsumoCreate
from modules.gestion_almacen_inusmos.movimiento_insumos.repository_interface import MovimientoInsumoRepositoryInterface

class MovimientoInsumoRepository(MovimientoInsumoRepositoryInterface):
    def get_all(self, db: Session) -> List[MovimientoInsumo]:
        return db.query(MovimientoInsumo).filter(MovimientoInsumo.anulado == False).all()

    def get_by_id(self, db: Session, movimiento_id: int) -> Optional[MovimientoInsumo]:
        return db.query(MovimientoInsumo).filter(MovimientoInsumo.id_movimiento == movimiento_id, MovimientoInsumo.anulado == False).first()

    def create(self, db: Session, movimiento: MovimientoInsumoCreate) -> MovimientoInsumo:
        db_movimiento = MovimientoInsumo(**movimiento.model_dump())
        db.add(db_movimiento)
        db.commit()
        db.refresh(db_movimiento)
        return db_movimiento

