from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from modules.recetas.schemas import Receta, RecetaCreate, RecetaUpdate
from modules.recetas.repository import RecetaRepository
from modules.recetas.service_interface import RecetaServiceInterface

class RecetaService(RecetaServiceInterface):
    def __init__(self):
        self.repository = RecetaRepository()

    def get_all(self, db: Session) -> List[Receta]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, receta_id: int) -> Receta:
        receta = self.repository.get_by_id(db, receta_id)
        if not receta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
        return receta

    def create(self, db: Session, receta: RecetaCreate) -> Receta:
        return self.repository.create(db, receta)

    def update(self, db: Session, receta_id: int, receta: RecetaUpdate) -> Receta:
        receta_actualizada = self.repository.update(db, receta_id, receta)
        if not receta_actualizada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
        return receta_actualizada

    def delete(self, db: Session, receta_id: int):
        if not self.repository.delete(db, receta_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
        return {"message": "Receta anulada correctamente"}

