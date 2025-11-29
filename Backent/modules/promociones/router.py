from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from database import get_db
from .service import PromocionService
from .schemas import (
    PromocionCreate, PromocionUpdate, PromocionResponse,
    SugerenciaPromocion, EstadisticasPromociones, ActivarPromocionRequest
)
from utils.standard_responses import (
    api_response_ok, 
    api_response_bad_request, 
    api_response_internal_server_error,
    api_response_not_found
)

router = APIRouter(
    prefix="/v1/promociones",
    tags=["Promociones"]
)

@router.get("/estadisticas")
def get_estadisticas(db: Session = Depends(get_db)):
    """Obtiene estadísticas generales de promociones"""
    try:
        service = PromocionService(db)
        stats = service.get_estadisticas()
        return api_response_ok(stats.model_dump())
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.get("/sugerencias")
def get_sugerencias(
    dias_alerta: int = Query(default=7, ge=1, le=30, description="Días antes del vencimiento para alertar"),
    db: Session = Depends(get_db)
):
    """Genera sugerencias de promociones basadas en productos por vencer"""
    try:
        service = PromocionService(db)
        sugerencias = service.generar_sugerencias(dias_alerta)
        return api_response_ok([s.model_dump() for s in sugerencias])
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.post("/sugerencias/activar")
def activar_sugerencia(
    request: ActivarPromocionRequest,
    db: Session = Depends(get_db)
):
    """Activa una promoción basada en una sugerencia"""
    try:
        service = PromocionService(db)
        
        # Crear la sugerencia manualmente para pasarla al servicio
        sugerencia = SugerenciaPromocion(
            id_producto=request.id_producto,
            nombre_producto="",
            stock_actual=0,
            precio_venta=0,
            dias_hasta_vencimiento=0,
            tipo_sugerido=request.tipo_promocion,
            titulo_sugerido=request.titulo or "Promoción Especial",
            descripcion_sugerida=request.descripcion or "Promoción activada manualmente",
            descuento_sugerido=request.porcentaje_descuento,
            ahorro_potencial=0,
            urgencia="MEDIA"
        )
        
        promocion = service.crear_desde_sugerencia(sugerencia, request.fecha_fin)
        return api_response_ok(promocion.model_dump())
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.get("/activas")
def get_activas(db: Session = Depends(get_db)):
    """Obtiene todas las promociones activas"""
    try:
        service = PromocionService(db)
        promociones = service.get_activas()
        return api_response_ok([p.model_dump() for p in promociones])
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.get("")
def get_all(db: Session = Depends(get_db)):
    """Obtiene todas las promociones"""
    try:
        service = PromocionService(db)
        promociones = service.get_all()
        return api_response_ok([p.model_dump() for p in promociones])
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.get("/{promocion_id}")
def get_by_id(promocion_id: int, db: Session = Depends(get_db)):
    """Obtiene una promoción por ID"""
    try:
        service = PromocionService(db)
        promocion = service.get_by_id(promocion_id)
        if not promocion:
            return api_response_not_found("Promoción no encontrada")
        return api_response_ok(promocion.model_dump())
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.post("")
def create(data: PromocionCreate, db: Session = Depends(get_db)):
    """Crea una nueva promoción"""
    try:
        service = PromocionService(db)
        promocion = service.create(data)
        return api_response_ok(promocion.model_dump())
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.put("/{promocion_id}")
def update(promocion_id: int, data: PromocionUpdate, db: Session = Depends(get_db)):
    """Actualiza una promoción"""
    try:
        service = PromocionService(db)
        promocion = service.update(promocion_id, data)
        if not promocion:
            return api_response_not_found("Promoción no encontrada")
        return api_response_ok(promocion.model_dump())
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.post("/{promocion_id}/activar")
def activar(promocion_id: int, db: Session = Depends(get_db)):
    """Activa una promoción"""
    try:
        service = PromocionService(db)
        promocion = service.activar(promocion_id)
        if not promocion:
            return api_response_not_found("Promoción no encontrada")
        return api_response_ok(promocion.model_dump())
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.post("/{promocion_id}/pausar")
def pausar(promocion_id: int, db: Session = Depends(get_db)):
    """Pausa una promoción"""
    try:
        service = PromocionService(db)
        promocion = service.pausar(promocion_id)
        if not promocion:
            return api_response_not_found("Promoción no encontrada")
        return api_response_ok(promocion.model_dump())
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.post("/{promocion_id}/cancelar")
def cancelar(promocion_id: int, db: Session = Depends(get_db)):
    """Cancela una promoción"""
    try:
        service = PromocionService(db)
        promocion = service.cancelar(promocion_id)
        if not promocion:
            return api_response_not_found("Promoción no encontrada")
        return api_response_ok(promocion.model_dump())
    except Exception as e:
        return api_response_internal_server_error(str(e))

@router.delete("/{promocion_id}")
def delete(promocion_id: int, db: Session = Depends(get_db)):
    """Elimina (anula) una promoción"""
    try:
        service = PromocionService(db)
        if service.delete(promocion_id):
            return api_response_ok("Promoción eliminada correctamente")
        return api_response_not_found("Promoción no encontrada")
    except Exception as e:
        return api_response_internal_server_error(str(e))
