from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from modules.movimiento_insumos.schemas import MovimientoInsumo
from modules.movimiento_insumos.service import MovimientoInsumoService
from utils.standard_responses import api_response_ok, api_response_not_found

router = APIRouter()

service = MovimientoInsumoService()

@router.get("/", response_model=List[MovimientoInsumo])
def get_all_movimientos_insumos(db: Session = Depends(get_db)):
    movimientos = service.get_all(db)
    return api_response_ok(movimientos)

@router.get("/{movimiento_id}", response_model=MovimientoInsumo)
def get_movimiento_insumo_by_id(movimiento_id: int, db: Session = Depends(get_db)):
    try:
        movimiento = service.get_by_id(db, movimiento_id)
        return api_response_ok(movimiento)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

