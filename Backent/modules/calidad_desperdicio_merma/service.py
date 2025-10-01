from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from modules.calidad_desperdicio_merma.schemas import Merma, MermaCreate, MermaUpdate
from modules.calidad_desperdicio_merma.repository import MermaRepository
from modules.calidad_desperdicio_merma.service_interface import MermaServiceInterface

class MermaService(MermaServiceInterface):
    def __init__(self):
        self.repository = MermaRepository()

    def get_all(self, db: Session) -> List[Merma]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, merma_id: int) -> Merma:
        merma = self.repository.get_by_id(db, merma_id)
        if not merma:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de merma no encontrado")
        return merma

    def create(self, db: Session, merma: MermaCreate) -> Merma:
        return self.repository.create(db, merma)

    def update(self, db: Session, merma_id: int, merma: MermaUpdate) -> Merma:
        merma_actualizada = self.repository.update(db, merma_id, merma)
        if not merma_actualizada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de merma no encontrado")
        return merma_actualizada

    def delete(self, db: Session, merma_id: int) -> dict:
        if not self.repository.delete(db, merma_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de merma no encontrado")
        return {"message": "Registro de merma anulado correctamente"}

