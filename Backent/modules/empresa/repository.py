# Lógica de acceso a datos para el módulo de empresa

from sqlalchemy.orm import Session
from modules.empresa.model import Empresa
from modules.empresa.schemas import EmpresaCreate, EmpresaUpdate

class EmpresaRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_empresa(self, empresa_id: int):
        return self.db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()

    def get_empresa_by_ruc(self, ruc: str):
        return self.db.query(Empresa).filter(Empresa.ruc == ruc).first()

    def get_empresas(self, skip: int = 0, limit: int = 100):
        return self.db.query(Empresa).offset(skip).limit(limit).all()

    def create_empresa(self, empresa: EmpresaCreate):
        db_empresa = Empresa(**empresa.model_dump())
        self.db.add(db_empresa)
        self.db.commit()
        self.db.refresh(db_empresa)
        return db_empresa

    def update_empresa(self, empresa_id: int, empresa: EmpresaUpdate):
        db_empresa = self.db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
        if not db_empresa:
            return None

        update_data = empresa.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_empresa, key, value)

        self.db.commit()
        self.db.refresh(db_empresa)
        return db_empresa

    def delete_empresa(self, empresa_id: int):
        db_empresa = self.db.query(Empresa).filter(Empresa.id_empresa == empresa_id).first()
        if not db_empresa:
            return None

        # Soft delete
        db_empresa.estado = False
        self.db.add(db_empresa)
        self.db.commit()
        self.db.refresh(db_empresa)
        return db_empresa
