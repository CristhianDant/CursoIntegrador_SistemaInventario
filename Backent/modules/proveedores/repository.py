from sqlalchemy.orm import Session
from .model import Proveedor
from .schemas import ProveedorCreate, ProveedorUpdate

class ProveedorRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_proveedor(self, proveedor_id: int):
        return self.db.query(Proveedor).filter(Proveedor.id_proveedor == proveedor_id).first()

    def get_proveedor_by_ruc_dni(self, ruc_dni: str):
        return self.db.query(Proveedor).filter(Proveedor.ruc_dni == ruc_dni).first()

    def get_proveedores(self, skip: int = 0, limit: int = 100):
        return self.db.query(Proveedor).filter(Proveedor.anulado.is_(False)).offset(skip).limit(limit).all()

    def create_proveedor(self, proveedor: ProveedorCreate):
        db_proveedor = Proveedor(**proveedor.model_dump())
        self.db.add(db_proveedor)
        self.db.commit()
        self.db.refresh(db_proveedor)
        return db_proveedor

    def update_proveedor(self, proveedor_id: int, proveedor: ProveedorUpdate):
        db_proveedor = self.db.query(Proveedor).filter(Proveedor.id_proveedor == proveedor_id).first()
        if not db_proveedor:
            return None

        update_data = proveedor.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_proveedor, key, value)

        self.db.commit()
        self.db.refresh(db_proveedor)
        return db_proveedor

    def delete_proveedor(self, proveedor_id: int):
        db_proveedor = self.db.query(Proveedor).filter(Proveedor.id_proveedor == proveedor_id).first()
        if not db_proveedor:
            return None

        db_proveedor.anulado = True
        self.db.commit()
        self.db.refresh(db_proveedor)
        return db_proveedor
