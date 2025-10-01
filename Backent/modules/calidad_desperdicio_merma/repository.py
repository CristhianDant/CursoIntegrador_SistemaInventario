from typing import List, Optional
from sqlalchemy.orm import Session
from modules.calidad_desperdicio_merma.model import CalidadDesperdicioMerma
from modules.calidad_desperdicio_merma.schemas import MermaCreate, MermaUpdate
from modules.calidad_desperdicio_merma.repository_interface import MermaRepositoryInterface

class MermaRepository(MermaRepositoryInterface):
    def get_all(self, db: Session) -> List[CalidadDesperdicioMerma]:
        return db.query(CalidadDesperdicioMerma).filter(CalidadDesperdicioMerma.anulado == False).all()

    def get_by_id(self, db: Session, merma_id: int) -> Optional[CalidadDesperdicioMerma]:
        return db.query(CalidadDesperdicioMerma).filter(CalidadDesperdicioMerma.id_merma == merma_id, CalidadDesperdicioMerma.anulado == False).first()

    def create(self, db: Session, merma: MermaCreate) -> CalidadDesperdicioMerma:
        db_merma = CalidadDesperdicioMerma(**merma.model_dump())
        db.add(db_merma)
        db.commit()
        db.refresh(db_merma)
        return db_merma

    def update(self, db: Session, merma_id: int, merma: MermaUpdate) -> Optional[CalidadDesperdicioMerma]:
        db_merma = self.get_by_id(db, merma_id)
        if db_merma:
            update_data = merma.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_merma, key, value)
            db.commit()
            db.refresh(db_merma)
        return db_merma

    def delete(self, db: Session, merma_id: int) -> bool:
        db_merma = self.get_by_id(db, merma_id)
        if db_merma:
            db_merma.anulado = True
            db.commit()
            return True
        return False

