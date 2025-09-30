from sqlalchemy.orm import Session
from modules.insumo.model import Insumo
from modules.insumo.schemas import InsumoCreate, InsumoUpdate

class InsumoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_insumo(self, insumo_id: int) -> Insumo | None:
        return self.db.query(Insumo).filter(Insumo.id_insumo == insumo_id, Insumo.anulado == False).first()

    def get_insumos(self, skip: int = 0, limit: int = 100) -> list[Insumo]:
        return self.db.query(Insumo).filter(Insumo.anulado == False).offset(skip).limit(limit).all()

    def create_insumo(self, insumo: InsumoCreate) -> Insumo:
        db_insumo = Insumo(**insumo.model_dump())
        self.db.add(db_insumo)
        self.db.commit()
        self.db.refresh(db_insumo)
        return db_insumo

    def update_insumo(self, insumo_id: int, insumo: InsumoUpdate) -> Insumo | None:
        db_insumo = self.get_insumo(insumo_id)
        if db_insumo:
            update_data = insumo.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_insumo, key, value)
            self.db.commit()
            self.db.refresh(db_insumo)
        return db_insumo

    def delete_insumo(self, insumo_id: int) -> Insumo | None:
        db_insumo = self.db.query(Insumo).filter(Insumo.id_insumo == insumo_id).first()
        if db_insumo:
            db_insumo.anulado = True
            self.db.commit()
            self.db.refresh(db_insumo)
        return db_insumo
