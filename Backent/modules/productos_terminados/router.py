from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from modules.productos_terminados.schemas import ProductoTerminado, ProductoTerminadoCreate, ProductoTerminadoUpdate
from modules.productos_terminados.service import ProductoTerminadoService

router = APIRouter(
    prefix="/productos_terminados",
    tags=["productos_terminados"],
    responses={404: {"description": "Not found"}},
)

service = ProductoTerminadoService()

@router.get("/", response_model=List[ProductoTerminado])
def get_all_productos_terminados(db: Session = Depends(get_db)):
    return service.get_all(db)

@router.get("/{producto_id}", response_model=ProductoTerminado)
def get_producto_terminado_by_id(producto_id: int, db: Session = Depends(get_db)):
    producto = service.get_by_id(db, producto_id)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto terminado no encontrado")
    return producto

@router.post("/", response_model=ProductoTerminado, status_code=201)
def create_producto_terminado(producto: ProductoTerminadoCreate, db: Session = Depends(get_db)):
    return service.create(db, producto)

@router.put("/{producto_id}", response_model=ProductoTerminado)
def update_producto_terminado(producto_id: int, producto_update: ProductoTerminadoUpdate, db: Session = Depends(get_db)):
    producto = service.update(db, producto_id, producto_update)
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto terminado no encontrado")
    return producto

@router.delete("/{producto_id}", status_code=204)
def delete_producto_terminado(producto_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, producto_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Producto terminado no encontrado")
    return

