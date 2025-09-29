from sqlalchemy.orm import Session
from modules.insumo.model import Insumo
from modules.insumo.schemas import InsumoCreate, InsumoUpdate

def get_insumo(db: Session, insumo_id: int):
    return db.query(Insumo).filter_by(id_insumo=insumo_id).filter(Insumo.anulado.is_(False)).first()

def get_insumos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Insumo).filter(Insumo.anulado.is_(False)).offset(skip).limit(limit).all()

def create_insumo(db: Session, insumo: InsumoCreate):
    db_insumo = Insumo(**insumo.model_dump())
    db.add(db_insumo)
    db.commit()
    db.refresh(db_insumo)
    return db_insumo

def update_insumo(db: Session, insumo_id: int, insumo: InsumoUpdate):
    db_insumo = db.query(Insumo).filter_by(id_insumo=insumo_id).filter(Insumo.anulado.is_(False)).first()
    if db_insumo:
        update_data = insumo.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_insumo, key, value)
        db.commit()
        db.refresh(db_insumo)
    return db_insumo

def delete_insumo(db: Session, insumo_id: int):
    db_insumo = db.query(Insumo).filter_by(id_insumo=insumo_id).first()
    if db_insumo:
        db_insumo.anulado = True
        db.commit()
        db.refresh(db_insumo)
    return db_insumo
