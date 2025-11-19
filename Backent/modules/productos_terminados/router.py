from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from modules.productos_terminados.schemas import ProductoTerminado, ProductoTerminadoCreate, ProductoTerminadoUpdate
from modules.productos_terminados.service import ProductoTerminadoService
from utils.standard_responses import api_response_not_found, api_response_ok

router = APIRouter()

service = ProductoTerminadoService()

@router.get("/", response_model=List[ProductoTerminado])
def get_all_productos_terminados(db: Session = Depends(get_db)):
    productos = service.get_all(db)
    return api_response_ok(productos)

@router.get("/{producto_id}", response_model=ProductoTerminado)
def get_producto_terminado_by_id(producto_id: int, db: Session = Depends(get_db)):
    producto = service.get_by_id(db, producto_id)
    if producto is None:
        return api_response_not_found("Producto terminado no encontrado")
    return api_response_ok(producto)

@router.post("/", response_model=ProductoTerminado, status_code=201)
def create_producto_terminado(producto: ProductoTerminadoCreate, db: Session = Depends(get_db)):
    try:
        nuevo_producto = service.create(db, producto)
        return api_response_ok(nuevo_producto)
    except ValueError as ve:
        return api_response_not_found(str(ve))
    except Exception as e:
        return api_response_not_found(str(e))

@router.put("/{producto_id}", response_model=ProductoTerminado)
def update_producto_terminado(producto_id: int, producto_update: ProductoTerminadoUpdate, db: Session = Depends(get_db)):
    try:
        producto = service.update(db, producto_id, producto_update)
        if producto is None:
            return api_response_not_found("Producto terminado no encontrado")
        return api_response_ok(producto)
    except ValueError as ve:
        return api_response_not_found(str(ve))
    except Exception as e:
        return api_response_not_found(str(e))

@router.delete("/{producto_id}")
def delete_producto_terminado(producto_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, producto_id)
    if not deleted:
        return api_response_not_found("Producto terminado no encontrado")
    return api_response_ok({"detail": "Producto terminado eliminado"})
