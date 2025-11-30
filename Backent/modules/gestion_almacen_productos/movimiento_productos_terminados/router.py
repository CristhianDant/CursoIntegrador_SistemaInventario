from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from modules.gestion_almacen_productos.movimiento_productos_terminados.schemas import MovimientoProductoTerminado
from modules.gestion_almacen_productos.movimiento_productos_terminados.service import MovimientoProductoTerminadoService
from modules.productos_terminados.repository import ProductoTerminadoRepository
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()

service = MovimientoProductoTerminadoService()
producto_repository = ProductoTerminadoRepository()

@router.get("/", response_model=List[MovimientoProductoTerminado])
def get_all_movimientos_productos_terminados(db: Session = Depends(get_db)):
    movimientos = service.get_all(db)
    return api_response_ok(movimientos)

@router.get("/{movimiento_id}", response_model=MovimientoProductoTerminado)
def get_movimiento_producto_terminado_by_id(movimiento_id: int, db: Session = Depends(get_db)):
    try:
        movimiento = service.get_by_id(db, movimiento_id)
        return api_response_ok(movimiento)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

