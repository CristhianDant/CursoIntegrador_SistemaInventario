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
    try:
        db_insumo = service.create_insumo(insumo)
        return api_response_ok(db_insumo)
    except ValueError as e:
        return api_response_not_found(str(e))
    except Exception as e:
        return api_response_not_found(f"Error al crear el insumo: {str(e)}")

@router.get("/", response_model=List[Insumo])
def read_insumos(skip: int = 0, limit: int = 100, service: InsumoService = Depends(get_insumo_service)):
    insumos = service.get_insumos(skip, limit)
    return api_response_ok(insumos)

@router.get("/precios/ultimos")
def get_ultimos_precios(service: InsumoService = Depends(get_insumo_service)):
    """
    Obtiene el último precio de compra de cada insumo.
    Retorna un diccionario {id_insumo: precio_unitario}
    """
    try:
        precios = service.get_ultimos_precios()
        return api_response_ok(precios)
    except Exception as e:
        return api_response_not_found(f"Error al obtener precios: {str(e)}")

@router.get("/{insumo_id}", response_model=Insumo)
def read_insumo(insumo_id: int, service: InsumoService = Depends(get_insumo_service)):
    db_insumo = service.get_insumo(insumo_id)
    if db_insumo is None:
        return api_response_not_found("Insumo no encontrado")
    return api_response_ok(db_insumo)

@router.put("/{insumo_id}", response_model=Insumo)
def update_insumo(insumo_id: int, insumo: InsumoUpdate, service: InsumoService = Depends(get_insumo_service)):
    try:
        db_insumo = service.update_insumo(insumo_id, insumo)
        if db_insumo is None:
            return api_response_not_found("Insumo no encontrado")
        return api_response_ok(db_insumo)
    except ValueError as ve:
        return api_response_not_found(str(ve))
    except Exception as e:
        return api_response_not_found(f"Error al actualizar el insumo: {str(e)}")

@router.delete("/{insumo_id}", response_model=Insumo)
def delete_insumo(insumo_id: int, service: InsumoService = Depends(get_insumo_service)):
    db_insumo = service.delete_insumo(insumo_id)
    if db_insumo is None:
        return api_response_not_found("Insumo no encontrado")
    return api_response_ok(db_insumo)
