from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from modules.insumo.schemas import Insumo, InsumoCreate, InsumoUpdate
from modules.insumo.service import InsumoService
from typing import List
from utils.standard_responses import api_response_ok, api_response_not_found

router = APIRouter()

def get_insumo_service(db: Session = Depends(get_db)) -> InsumoService:
    return InsumoService(db)

@router.post("/", response_model=Insumo)
def create_insumo(insumo: InsumoCreate, service: InsumoService = Depends(get_insumo_service)):
    nuevo_insumo = service.create_insumo(insumo)
    return api_response_ok(nuevo_insumo)

@router.get("/", response_model=List[Insumo])
def read_insumos(skip: int = 0, limit: int = 100, service: InsumoService = Depends(get_insumo_service)):
    insumos = service.get_insumos(skip, limit)
    return api_response_ok(insumos)

@router.get("/{insumo_id}", response_model=Insumo)
def read_insumo(insumo_id: int, service: InsumoService = Depends(get_insumo_service)):
    db_insumo = service.get_insumo(insumo_id)
    if db_insumo is None:
        return api_response_not_found("Insumo no encontrado")
    return api_response_ok(db_insumo)

@router.put("/{insumo_id}", response_model=Insumo)
def update_insumo(insumo_id: int, insumo: InsumoUpdate, service: InsumoService = Depends(get_insumo_service)):
    db_insumo = service.update_insumo(insumo_id, insumo)
    if db_insumo is None:
        return api_response_not_found("Insumo no encontrado")
    return api_response_ok(db_insumo)

@router.delete("/{insumo_id}", response_model=Insumo)
def delete_insumo(insumo_id: int, service: InsumoService = Depends(get_insumo_service)):
    db_insumo = service.delete_insumo(insumo_id)
    if db_insumo is None:
        return api_response_not_found("Insumo no encontrado")
    return api_response_ok(db_insumo)
