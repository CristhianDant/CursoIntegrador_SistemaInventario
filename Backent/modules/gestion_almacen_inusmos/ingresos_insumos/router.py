from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from modules.gestion_almacen_inusmos.ingresos_insumos.schemas import IngresoProducto, IngresoProductoCreate, IngresoProductoUpdate, InsumoLotesFefoResponse
from modules.gestion_almacen_inusmos.ingresos_insumos.service import IngresoProductoService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()

service = IngresoProductoService()

@router.get("/", response_model=List[IngresoProducto])
def get_all_ingresos_productos(db: Session = Depends(get_db)):
    ingresos = service.get_all(db)
    return api_response_ok(ingresos)

@router.get("/{ingreso_id}", response_model=IngresoProducto)
def get_ingreso_producto_by_id(ingreso_id: int, db: Session = Depends(get_db)):
    try:
        ingreso = service.get_by_id(db, ingreso_id)
        return api_response_ok(ingreso)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

@router.post("/", response_model=IngresoProducto)
def create_ingreso_producto(ingreso: IngresoProductoCreate, db: Session = Depends(get_db)):
    try:
        new_ingreso = service.create(db, ingreso)
        return api_response_ok(new_ingreso)
    except Exception as e:
        return api_response_bad_request(str(e))

@router.put("/{ingreso_id}", response_model=IngresoProducto)
def update_ingreso_producto(ingreso_id: int, ingreso: IngresoProductoUpdate, db: Session = Depends(get_db)):
    try:
        updated_ingreso = service.update(db, ingreso_id, ingreso)
        return api_response_ok(updated_ingreso)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))

@router.delete("/{ingreso_id}")
def delete_ingreso_producto(ingreso_id: int, db: Session = Depends(get_db)):
    try:
        response = service.delete(db, ingreso_id)
        return api_response_ok(response)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

@router.get("/lotes-fefo/{id_insumo}", response_model=InsumoLotesFefoResponse)
def get_lotes_fefo(id_insumo: int, db: Session = Depends(get_db)):
    """
    Obtiene todos los lotes (ingresos_detalle) de un insumo ordenados por FEFO.
    
    Ordenamiento:
    1. Cantidad restante (DESC) - Disponibilidad
    2. Fecha vencimiento (ASC) - FEFO (First Expired, First Out)
    
    Solo retorna lotes con cantidad_restante > 0
    """
    try:
        lotes_fefo = service.get_lotes_fefo(db, id_insumo)
        return api_response_ok(lotes_fefo)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))

