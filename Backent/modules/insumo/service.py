from sqlalchemy.orm import Session
from modules.insumo import repository
from modules.insumo.schemas import InsumoCreate, InsumoUpdate

def create_insumo(db: Session, insumo: InsumoCreate):
    return repository.create_insumo(db=db, insumo=insumo)

def get_insumos(db: Session, skip: int = 0, limit: int = 100):
    return repository.get_insumos(db, skip=skip, limit=limit)

def get_insumo(db: Session, insumo_id: int):
    return repository.get_insumo(db, insumo_id)

def update_insumo(db: Session, insumo_id: int, insumo: InsumoUpdate):
    return repository.update_insumo(db, insumo_id, insumo)

def delete_insumo(db: Session, insumo_id: int):
    return repository.delete_insumo(db, insumo_id)
