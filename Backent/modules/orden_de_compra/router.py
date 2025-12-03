from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import Base
from datetime import datetime, date
from typing import List, Optional
from database import get_db
from modules.orden_de_compra.schemas import (
    OrdenDeCompra, OrdenDeCompraCreate, OrdenDeCompraUpdate,
    SugerenciaCompraResponse, GenerarOrdenDesdesugerenciaRequest,
    EnviarEmailProveedorRequest, EnviarEmailProveedorResponse
)
from modules.orden_de_compra.service import OrdenDeCompraService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()

service = OrdenDeCompraService()

# ==================== SUGERENCIAS DE COMPRA (FC-10) ====================

@router.get("/sugerencia", response_model=SugerenciaCompraResponse)
def get_sugerencias_compra(
    dias_proyeccion: int = Query(7, ge=1, le=90, description="Días de proyección para calcular necesidades"),
    urgencia: Optional[str] = Query(None, description="Filtrar por urgencia: 'inmediata' o 'normal'"),
    id_proveedor: Optional[int] = Query(None, description="Filtrar por proveedor específico"),
    db: Session = Depends(get_db)
):
    """
    Genera una lista de sugerencias de compra basada en:
    - Stock actual vs stock mínimo
    - Consumo promedio diario (últimos 30 días)
    - Productos por vencer (próximos 7 días)
    
    Urgencia:
    - 'inmediata' (rojo): menos de 7 días de stock o stock en 0
    - 'normal' (verde): más de 7 días de stock
    """
    try:
        sugerencias = service.generar_sugerencias_compra(
            db=db,
            dias_proyeccion=dias_proyeccion,
            urgencia=urgencia,
            id_proveedor=id_proveedor
        )
        return api_response_ok(sugerencias)
    except Exception as e:
        return api_response_bad_request(str(e))


@router.post("/generar-orden-sugerida", response_model=OrdenDeCompra)
def generar_orden_desde_sugerencia(
    request: GenerarOrdenDesdesugerenciaRequest,
    db: Session = Depends(get_db)
):
    """
    Genera una orden de compra a partir de items sugeridos.
    Permite seleccionar qué items incluir en la orden.
    """
    try:
        orden = service.generar_orden_desde_sugerencia(db, request)
        return api_response_ok(orden)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))


@router.post("/enviar-email-proveedor", response_model=EnviarEmailProveedorResponse)
def enviar_email_proveedor(
    request: EnviarEmailProveedorRequest,
    db: Session = Depends(get_db)
):
    """
    Envía un email al proveedor con la lista de insumos a cotizar.
    El email incluye: nombre de empresa, lista de insumos, cantidades,
    unidades y último precio de referencia.
    """
    try:
        resultado = service.enviar_email_proveedor(db, request)
        return api_response_ok(resultado)
    except HTTPException as e:
        if e.status_code == 404:
            return api_response_not_found(str(e.detail))
        return api_response_bad_request(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))


# ==================== CRUD ÓRDENES DE COMPRA ====================

@router.get("/", response_model=List[OrdenDeCompra])
def get_all_ordenes_compra(db: Session = Depends(get_db), activas_solo: bool = Query(True, description="Si True, solo retorna órdenes no anuladas")):
    ordenes = service.get_all(db, activas_solo=activas_solo)
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

