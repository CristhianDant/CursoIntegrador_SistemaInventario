from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .repository import ProveedorRepository
from .schemas import ProveedorCreate, ProveedorUpdate

class ProveedorService:
    def __init__(self, db: Session):
        self.repository = ProveedorRepository(db)

    def create_proveedor(self, proveedor: ProveedorCreate):
        db_proveedor = self.repository.get_proveedor_by_ruc_dni(ruc_dni=proveedor.ruc_dni)
        if db_proveedor:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RUC/DNI ya registrado")
        return self.repository.create_proveedor(proveedor=proveedor)

    def get_proveedores(self, skip: int = 0, limit: int = 100):
        return self.repository.get_proveedores(skip=skip, limit=limit)

    def get_proveedor(self, proveedor_id: int):
        db_proveedor = self.repository.get_proveedor(proveedor_id=proveedor_id)
        if db_proveedor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
        return db_proveedor

    def update_proveedor(self, proveedor_id: int, proveedor: ProveedorUpdate):
        db_proveedor = self.repository.get_proveedor(proveedor_id=proveedor_id)
        if db_proveedor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")

        if proveedor.ruc_dni:
            existing_proveedor = self.repository.get_proveedor_by_ruc_dni(ruc_dni=proveedor.ruc_dni)
            if existing_proveedor and existing_proveedor.id_proveedor != proveedor_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="RUC/DNI ya pertenece a otro proveedor")

        return self.repository.update_proveedor(proveedor_id=proveedor_id, proveedor=proveedor)

    def delete_proveedor(self, proveedor_id: int):
        db_proveedor = self.repository.get_proveedor(proveedor_id=proveedor_id)
        if db_proveedor is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
        return self.repository.delete_proveedor(proveedor_id=proveedor_id)

