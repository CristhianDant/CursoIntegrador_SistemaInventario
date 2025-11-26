from typing import List, Optional
from sqlalchemy.orm import Session
from modules.orden_de_compra.model import OrdenDeCompra, OrdenDeCompraDetalle
from modules.orden_de_compra.schemas import OrdenDeCompraCreate, OrdenDeCompraUpdate
from modules.orden_de_compra.repository_interface import OrdenDeCompraRepositoryInterface

class OrdenDeCompraRepository(OrdenDeCompraRepositoryInterface):
    def get_all(self, db: Session, activas_solo: bool = True) -> List[OrdenDeCompra]:
        if activas_solo:
            ordenes = db.query(OrdenDeCompra).filter(OrdenDeCompra.anulado == False).all()
        else:
            # Cargar todas, incluyendo anuladas (para editar ingresos con órdenes anuladas)
            ordenes = db.query(OrdenDeCompra).all()
        # Forzar carga de detalles para cada orden
        for orden in ordenes:
            _ = orden.detalles
        return ordenes

    def get_by_id(self, db: Session, orden_id: int) -> Optional[OrdenDeCompra]:
        orden = db.query(OrdenDeCompra).filter(OrdenDeCompra.id_orden == orden_id, OrdenDeCompra.anulado == False).first()
        if orden:
            # Forzar carga de detalles
            _ = orden.detalles
        return orden

    def create(self, db: Session, orden: OrdenDeCompraCreate) -> OrdenDeCompra:
        orden_data = orden.model_dump(exclude={'detalles'})
        db_orden = OrdenDeCompra(**orden_data)

        db.add(db_orden)
        db.flush()

        for detalle_data in orden.detalles:
            db_detalle = OrdenDeCompraDetalle(**detalle_data.model_dump(), id_orden=db_orden.id_orden)
            db.add(db_detalle)

        db.commit()
        db.refresh(db_orden)
        # Forzar carga de detalles
        _ = db_orden.detalles
        return db_orden

    def update(self, db: Session, orden_id: int, orden: OrdenDeCompraUpdate) -> Optional[OrdenDeCompra]:
        db_orden = self.get_by_id(db, orden_id)
        if db_orden:
            update_data = orden.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                if key != "detalles":
                    setattr(db_orden, key, value)

            if "detalles" in update_data and update_data["detalles"] is not None:
                db.query(OrdenDeCompraDetalle).filter(OrdenDeCompraDetalle.id_orden == orden_id).delete()
                for detalle_data in orden.detalles:
                    db_detalle = OrdenDeCompraDetalle(**detalle_data.model_dump(), id_orden=orden_id)
                    db.add(db_detalle)

            db.commit()
            db.refresh(db_orden)
            # Forzar carga de detalles
            _ = db_orden.detalles
        return db_orden

    def delete(self, db: Session, orden_id: int) -> bool:
        db_orden = self.get_by_id(db, orden_id)
        if db_orden:
            db_orden.anulado = True
            db.commit()
            return True
        return False

