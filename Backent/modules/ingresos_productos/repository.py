from typing import List, Optional
from sqlalchemy.orm import Session
from modules.ingresos_productos.model import IngresoProducto, IngresoProductoDetalle
from modules.ingresos_productos.schemas import IngresoProductoCreate, IngresoProductoUpdate
from modules.ingresos_productos.repository_interface import IngresoProductoRepositoryInterface

class IngresoProductoRepository(IngresoProductoRepositoryInterface):
    def get_all(self, db: Session) -> List[IngresoProducto]:
        return db.query(IngresoProducto).filter(IngresoProducto.anulado == False).all()

    def get_by_id(self, db: Session, ingreso_id: int) -> Optional[IngresoProducto]:
        return db.query(IngresoProducto).filter(IngresoProducto.id_ingreso == ingreso_id, IngresoProducto.anulado == False).first()

    def create(self, db: Session, ingreso: IngresoProductoCreate) -> IngresoProducto:
        ingreso_data = ingreso.model_dump(exclude={'detalles'})
        db_ingreso = IngresoProducto(**ingreso_data)

        db.add(db_ingreso)
        db.flush()

        for detalle_data in ingreso.detalles:
            db_detalle = IngresoProductoDetalle(**detalle_data.model_dump(), id_ingreso=db_ingreso.id_ingreso)
            db.add(db_detalle)

        db.commit()
        db.refresh(db_ingreso)
        return db_ingreso

    def update(self, db: Session, ingreso_id: int, ingreso: IngresoProductoUpdate) -> Optional[IngresoProducto]:
        db_ingreso = self.get_by_id(db, ingreso_id)
        if db_ingreso:
            update_data = ingreso.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                if key != "detalles":
                    setattr(db_ingreso, key, value)

            if "detalles" in update_data and update_data["detalles"] is not None:
                db.query(IngresoProductoDetalle).filter(IngresoProductoDetalle.id_ingreso == ingreso_id).delete()
                for detalle_data in ingreso.detalles:
                    db_detalle = IngresoProductoDetalle(**detalle_data.model_dump(), id_ingreso=ingreso_id)
                    db.add(db_detalle)

            db.commit()
            db.refresh(db_ingreso)
        return db_ingreso

    def delete(self, db: Session, ingreso_id: int) -> bool:
        db_ingreso = self.get_by_id(db, ingreso_id)
        if db_ingreso:
            db_ingreso.anulado = True
            db.commit()
            return True
        return False

