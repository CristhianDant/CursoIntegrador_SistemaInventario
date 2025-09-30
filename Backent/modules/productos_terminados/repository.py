from sqlalchemy.orm import Session
from typing import List, Optional

from modules.productos_terminados.model import ProductoTerminado
from modules.productos_terminados.schemas import ProductoTerminadoCreate, ProductoTerminadoUpdate
from modules.productos_terminados.repository_interface import ProductoTerminadoRepositoryInterfaz


class ProductoTerminadoRepository(ProductoTerminadoRepositoryInterfaz):
    def get_all(self, db: Session) -> List[ProductoTerminado]:
        return db.query(ProductoTerminado).filter(ProductoTerminado.anulado == False).all()

    def get_by_id(self, db: Session, producto_id: int) -> Optional[ProductoTerminado]:
        return db.query(ProductoTerminado).filter(ProductoTerminado.id_producto == producto_id, ProductoTerminado.anulado == False).first()

    def create(self, db: Session, producto: ProductoTerminadoCreate) -> ProductoTerminado:
        db_producto = ProductoTerminado(**producto.dict())
        db.add(db_producto)
        db.commit()
        db.refresh(db_producto)
        return db_producto

    def update(self, db: Session, producto_id: int, producto_update: ProductoTerminadoUpdate) -> Optional[ProductoTerminado]:
        db_producto = self.get_by_id(db, producto_id)
        if db_producto:
            for key, value in producto_update.dict(exclude_unset=True).items():
                setattr(db_producto, key, value)
            db.commit()
            db.refresh(db_producto)
        return db_producto

    def delete(self, db: Session, producto_id: int) -> bool:
        db_producto = self.get_by_id(db, producto_id)
        if db_producto:
            db_producto.anulado = True
            db.commit()
            return True
        return False
