from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from modules.insumo.schemas import Insumo, InsumoCreate, InsumoUpdate
from modules.insumo.service import InsumoService
from typing import List

router = APIRouter(
    prefix="/insumos",
    tags=["insumos"],
)

def get_insumo_service(db: Session = Depends(get_db)) -> InsumoService:
    return InsumoService(db)

@router.post("/", response_model=Insumo)
def create_insumo(insumo: InsumoCreate, service: InsumoService = Depends(get_insumo_service)):
    return service.create_insumo(insumo)

@router.get("/", response_model=List[Insumo])
def read_insumos(skip: int = 0, limit: int = 100, service: InsumoService = Depends(get_insumo_service)):
    return service.get_insumos(skip, limit)

@router.get("/{insumo_id}", response_model=Insumo)
def read_insumo(insumo_id: int, service: InsumoService = Depends(get_insumo_service)):
    db_insumo = service.get_insumo(insumo_id)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return db_insumo

@router.put("/{insumo_id}", response_model=Insumo)
def update_insumo(insumo_id: int, insumo: InsumoUpdate, service: InsumoService = Depends(get_insumo_service)):
    db_insumo = service.update_insumo(insumo_id, insumo)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return db_insumo

@router.delete("/{insumo_id}", response_model=Insumo)
def delete_insumo(insumo_id: int, service: InsumoService = Depends(get_insumo_service)):
    db_insumo = service.delete_insumo(insumo_id)
    if db_insumo is None:
        raise HTTPException(status_code=404, detail="Insumo no encontrado")
    return db_insumo
