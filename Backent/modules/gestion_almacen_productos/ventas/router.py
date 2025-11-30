from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
from database import get_db
from modules.gestion_almacen_productos.ventas.service import VentasService
from modules.gestion_almacen_productos.ventas.schemas import (
    RegistrarVentaRequest,
    VentaResponse,
    VentaResumenResponse,
    ProductoDisponibleResponse,
    VentasDelDiaResponse
)
from utils.standard_responses import (
    api_response_ok,
    api_response_bad_request,
    api_response_internal_server_error
)

router = APIRouter(
    prefix="/ventas",
    tags=["Ventas"]
)

service = VentasService()


@router.post("/registrar", response_model=dict, status_code=status.HTTP_201_CREATED)
def registrar_venta(
    request: RegistrarVentaRequest,
    db: Session = Depends(get_db)
):
    """
    Registra una nueva venta y descuenta automáticamente el stock.
    
    **Flujo:**
    1. Valida stock disponible
    2. Crea venta y detalles
    3. Descuenta stock de productos terminados
    4. Crea movimientos de salida en Kardex
    
    **Ejemplo de request:**
    ```json
    {
        "items": [
            {
                "id_producto": 1,
                "cantidad": 5,
                "precio_unitario": 25.00,
                "descuento_porcentaje": 0
            }
        ],
        "metodo_pago": "efectivo",
        "observaciones": "Venta de mostrador"
    }
    ```
    """
    try:
        # TODO: Obtener id_user del token JWT
        id_user = 1  # Temporal
        
        venta = service.registrar_venta(db, request, id_user)
        return api_response_ok(venta.model_dump())
    except HTTPException as e:
        raise e
    except Exception as e:
        return api_response_internal_server_error(str(e))


@router.get("/del-dia", response_model=dict)
def obtener_ventas_del_dia(
    fecha: date = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las ventas de un día específico.
    Si no se especifica fecha, retorna las ventas del día actual.
    
    **Query params:**
    - `fecha` (opcional): Fecha en formato YYYY-MM-DD. Default: hoy
    
    **Ejemplo:**
    ```
    GET /ventas/del-dia?fecha=2025-11-29
    ```
    """
    try:
        if not fecha:
            fecha = date.today()
        
        ventas = service.get_ventas_del_dia(db, fecha)
        return api_response_ok(ventas.model_dump())
    except Exception as e:
        return api_response_internal_server_error(str(e))


@router.get("/{id_venta}", response_model=dict)
def obtener_venta_por_id(
    id_venta: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el detalle completo de una venta por su ID.
    Incluye todos los items vendidos y sus cantidades.
    
    **Path params:**
    - `id_venta`: ID de la venta
    """
    try:
        venta = service.get_venta_por_id(db, id_venta)
        return api_response_ok(venta.model_dump())
    except HTTPException as e:
        raise e
    except Exception as e:
        return api_response_internal_server_error(str(e))


@router.get("/productos-disponibles", response_model=dict)
def obtener_productos_disponibles(
    db: Session = Depends(get_db)
):
    """
    Obtiene productos disponibles para venta con descuentos sugeridos.
    
    **Implementa FC-09:** Descuento automático según antigüedad:
    - 1 día: 30% descuento
    - 2 días: 50% descuento
    - 3+ días: 70% descuento
    
    Solo retorna productos con stock > 0.
    """
    try:
        productos = service.get_productos_disponibles(db)
        return api_response_ok([p.model_dump() for p in productos])
    except Exception as e:
        return api_response_internal_server_error(str(e))


@router.post("/{id_venta}/anular", response_model=dict)
def anular_venta(
    id_venta: int,
    db: Session = Depends(get_db)
):
    """
    Anula una venta y restaura el stock de los productos.
    
    **Flujo:**
    1. Marca la venta como anulada
    2. Restaura el stock de cada producto
    3. Crea movimientos de entrada (compensación)
    
    **Path params:**
    - `id_venta`: ID de la venta a anular
    """
    try:
        # TODO: Obtener id_user del token JWT
        id_user = 1  # Temporal
        
        venta = service.anular_venta(db, id_venta, id_user)
        return api_response_ok(venta.model_dump())
    except HTTPException as e:
        raise e
    except Exception as e:
        return api_response_internal_server_error(str(e))
