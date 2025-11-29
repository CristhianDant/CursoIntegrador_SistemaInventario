from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from modules.movimiento_productos_terminados.schemas import MovimientoProductoTerminado, MovimientoProductoTerminadoCreate
from modules.movimiento_productos_terminados.service import MovimientoProductoTerminadoService
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

@router.post("/", response_model=MovimientoProductoTerminado, status_code=201)
def create_movimiento_producto_terminado(movimiento: MovimientoProductoTerminadoCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo movimiento de producto terminado y actualiza el stock.
    - PRODUCCION/ENTRADA: Incrementa stock_actual
    - VENTA/SALIDA/MERMA: Decrementa stock_actual
    """
    try:
        # Obtener el producto
        producto = producto_repository.get_by_id(db, movimiento.id_producto)
        if not producto:
            return api_response_not_found("Producto no encontrado")
        
        # Calcular nuevo stock según tipo de movimiento
        cantidad = float(movimiento.cantidad)
        tipo = movimiento.tipo_movimiento.value if hasattr(movimiento.tipo_movimiento, 'value') else str(movimiento.tipo_movimiento)
        
        if tipo in ["PRODUCCION", "ENTRADA"]:
            nuevo_stock = float(producto.stock_actual) + cantidad
        elif tipo in ["VENTA", "SALIDA", "MERMA"]:
            if float(producto.stock_actual) < cantidad:
                return api_response_bad_request("Stock insuficiente para realizar el movimiento")
            nuevo_stock = float(producto.stock_actual) - cantidad
        else:
            nuevo_stock = float(producto.stock_actual)
        
        # Crear el movimiento
        nuevo_movimiento = service.create(db, movimiento)
        
        # Actualizar stock del producto
        producto.stock_actual = nuevo_stock
        db.commit()
        
        return api_response_ok(nuevo_movimiento)
    except Exception as e:
        db.rollback()
        return api_response_bad_request(str(e))

