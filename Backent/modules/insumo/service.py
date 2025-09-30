from sqlalchemy.orm import Session
from modules.insumo.repository import InsumoRepository
from modules.insumo.schemas import Insumo, InsumoCreate, InsumoUpdate

class InsumoService:
    def __init__(self, db: Session):
        self.repository = InsumoRepository(db)

    def create_insumo(self, insumo: InsumoCreate) -> Insumo:
        db_insumo = self.repository.create_insumo(insumo)
        return Insumo.model_validate(db_insumo)

    def get_insumos(self, skip: int = 0, limit: int = 100) -> list[Insumo]:
        insumos = self.repository.get_insumos(skip, limit)
        return [Insumo.model_validate(i) for i in insumos]

    def get_insumo(self, insumo_id: int) -> Insumo | None:
        db_insumo = self.repository.get_insumo(insumo_id)
        if db_insumo:
            return Insumo.model_validate(db_insumo)
        return None

    def update_insumo(self, insumo_id: int, insumo: InsumoUpdate) -> Insumo | None:
        db_insumo = self.repository.update_insumo(insumo_id, insumo)
        if db_insumo:
            return Insumo.model_validate(db_insumo)
        return None

    def delete_insumo(self, insumo_id: int) -> Insumo | None:
        db_insumo = self.repository.delete_insumo(insumo_id)
        if db_insumo:
            return Insumo.model_validate(db_insumo)
        return None
