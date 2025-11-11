from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base
from datetime import datetime
from typing import List
from database import get_db
from modules.orden_de_compra.schemas import OrdenDeCompra, OrdenDeCompraCreate, OrdenDeCompraUpdate
from modules.orden_de_compra.service import OrdenDeCompraService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()

service = OrdenDeCompraService()

@router.get("/", response_model=List[OrdenDeCompra])
def get_all_ordenes_compra(db: Session = Depends(get_db)):
    ordenes = service.get_all(db)
    return api_response_ok(ordenes)

@router.get("/{orden_id}", response_model=OrdenDeCompra)
def get_orden_compra_by_id(orden_id: int, db: Session = Depends(get_db)):
    try:
        orden = service.get_by_id(db, orden_id)
        return api_response_ok(orden)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

@router.post("/", response_model=OrdenDeCompra)
def create_orden_compra(orden: OrdenDeCompraCreate, db: Session = Depends(get_db)):
    try:
        new_orden = service.create(db, orden)
        return api_response_ok(new_orden)
    except Exception as e:
        return api_response_bad_request(str(e))

@router.put("/{orden_id}", response_model=OrdenDeCompra)
def update_orden_compra(orden_id: int, orden: OrdenDeCompraUpdate, db: Session = Depends(get_db)):
    try:
        updated_orden = service.update(db, orden_id, orden)
        return api_response_ok(updated_orden)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))

@router.delete("/{orden_id}")
def delete_orden_compra(orden_id: int, db: Session = Depends(get_db)):
    try:
        response = service.delete(db, orden_id)
        return api_response_ok(response)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

