# Lógica de negocio para el módulo de empresa

from sqlalchemy.orm import Session
from modules.empresa.repository import EmpresaRepository
from modules.empresa.schemas import EmpresaCreate, EmpresaUpdate
from fastapi import HTTPException, status
from .service_interface import EmpresaServiceInterface


class EmpresaService(EmpresaServiceInterface):
    def __init__(self, db: Session):
        self.repository = EmpresaRepository(db)

    def create_empresa(self, empresa: EmpresaCreate):
        db_empresa = self.repository.get_empresa_by_ruc(ruc=empresa.ruc)
        if db_empresa:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RUC ya registrado")
        return self.repository.create_empresa(empresa=empresa)

    def get_empresas(self, skip: int = 0, limit: int = 100):
        return self.repository.get_empresas(skip=skip, limit=limit)

    def get_empresa(self, empresa_id: int):
        db_empresa = self.repository.get_empresa(empresa_id=empresa_id)
        if db_empresa is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada")
        return db_empresa

    def update_empresa(self, empresa_id: int, empresa: EmpresaUpdate):
        db_empresa = self.repository.get_empresa(empresa_id=empresa_id)
        if db_empresa is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada")

        if empresa.ruc:
            existing_empresa = self.repository.get_empresa_by_ruc(ruc=empresa.ruc)
            if existing_empresa and existing_empresa.id_empresa != empresa_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RUC ya pertenece a otra empresa")

        return self.repository.update_empresa(empresa_id=empresa_id, empresa=empresa)

    def delete_empresa(self, empresa_id: int):
        db_empresa = self.repository.get_empresa(empresa_id=empresa_id)
        if db_empresa is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada")
        return self.repository.delete_empresa(empresa_id=empresa_id)
