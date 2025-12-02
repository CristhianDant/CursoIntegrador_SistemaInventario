from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger
import time

from database import get_db
from .service import AlertasService
from .schemas import (
    NotificacionResponse,
    ResumenSemaforo,
    InsumoSemaforo,
    ResumenStockCritico,
    ListaUsarHoy,
    ResumenAlertas,
    ConfiguracionAlertasUpdate,
    ConfiguracionAlertasResponse,
    JobEjecutarResponse
)
from utils.standard_responses import api_response_ok

router = APIRouter()


def get_alertas_service(db: Session = Depends(get_db)) -> AlertasService:
    """Dependency injection para el servicio de alertas."""
    return AlertasService(db)


# ==================== CONFIGURACIÓN ====================

@router.get(
    "/configuracion",
    response_model=ConfiguracionAlertasResponse,
    summary="Obtener configuración de alertas"
)
def obtener_configuracion(
    id_empresa: int = Query(default=1, description="ID de la empresa"),
    service: AlertasService = Depends(get_alertas_service)
):
    """
    Obtiene la configuración actual de alertas de la empresa.
    Incluye días para semáforo (verde, amarillo, rojo), hora del job y email.
    """
    try:
        config = service.obtener_configuracion_alertas(id_empresa)
        return ConfiguracionAlertasResponse(
            id_empresa=id_empresa,
            **config
        )
    except Exception as e:
        logger.error(f"Error al obtener configuración: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/configuracion",
    response_model=ConfiguracionAlertasResponse,
    summary="Actualizar configuración de alertas"
)
def actualizar_configuracion(
    configuracion: ConfiguracionAlertasUpdate,
    id_empresa: int = Query(default=1, description="ID de la empresa"),
    service: AlertasService = Depends(get_alertas_service)
):
    """
    Actualiza la configuración de alertas de la empresa.
    """
    try:
        config = service.actualizar_configuracion_alertas(
            id_empresa=id_empresa,
            configuracion=configuracion.model_dump(exclude_none=True)
        )
        return ConfiguracionAlertasResponse(
            id_empresa=id_empresa,
            **config
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error al actualizar configuración: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== NOTIFICACIONES ====================

@router.get(
    "/notificaciones",
    response_model=List[NotificacionResponse],
    summary="Listar notificaciones"
)
def listar_notificaciones(
    tipo: Optional[str] = Query(
        default=None,
        description="Filtrar por tipo: STOCK_CRITICO, VENCIMIENTO_PROXIMO, USAR_HOY, VENCIDO"
    ),
    solo_no_leidas: bool = Query(default=False, description="Solo mostrar no leídas"),
    limit: int = Query(default=100, le=500, description="Límite de resultados"),
    service: AlertasService = Depends(get_alertas_service)
):
    """
    Obtiene lista de notificaciones activas con filtros opcionales.
    """
    try:
        return service.obtener_notificaciones(
            tipo=tipo,
            solo_no_leidas=solo_no_leidas,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error al listar notificaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/notificaciones/{id_notificacion}/leida",
    summary="Marcar notificación como leída"
)
def marcar_leida(
    id_notificacion: int,
    service: AlertasService = Depends(get_alertas_service)
):
    """Marca una notificación específica como leída."""
    try:
        result = service.marcar_notificacion_leida(id_notificacion)
        if result:
            return api_response_ok({
                "message": "Notificación marcada como leída",
                "id_notificacion": id_notificacion
            })
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al marcar notificación: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch(
    "/notificaciones/marcar-todas-leidas",
    summary="Marcar todas las notificaciones como leídas"
)
def marcar_todas_leidas(
    tipo: Optional[str] = Query(default=None, description="Filtrar por tipo"),
    service: AlertasService = Depends(get_alertas_service)
):
    """Marca todas las notificaciones (o de un tipo específico) como leídas."""
    try:
        count = service.marcar_todas_leidas(tipo=tipo)
        return api_response_ok({
            "message": f"{count} notificaciones marcadas como leídas",
            "cantidad": count
        })
    except Exception as e:
        logger.error(f"Error al marcar notificaciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/resumen",
    response_model=ResumenAlertas,
    summary="Resumen de alertas"
)
def obtener_resumen(service: AlertasService = Depends(get_alertas_service)):
    """Obtiene un resumen de alertas activas no leídas."""
    try:
        return service.obtener_resumen_alertas()
    except Exception as e:
        logger.error(f"Error al obtener resumen: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SEMÁFORO DE VENCIMIENTOS ====================

@router.get(
    "/semaforo",
    response_model=ResumenSemaforo,
    summary="Semáforo de vencimientos"
)
def obtener_semaforo(
    id_empresa: int = Query(default=1, description="ID de la empresa"),
    service: AlertasService = Depends(get_alertas_service)
):
    """
    Obtiene el semáforo completo de vencimientos.
    Clasifica los lotes en Verde (>15 días), Amarillo (7-15 días), Rojo (<7 días).
    """
    try:
        return service.obtener_semaforo_vencimientos(id_empresa)
    except Exception as e:
        logger.error(f"Error al obtener semáforo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/semaforo/rojo",
    response_model=List[InsumoSemaforo],
    summary="Items en estado rojo (crítico)"
)
def obtener_items_rojos(
    id_empresa: int = Query(default=1, description="ID de la empresa"),
    service: AlertasService = Depends(get_alertas_service)
):
    """
    Obtiene solo los items en estado rojo (vencen en menos de 7 días).
    Estos deben usarse con prioridad máxima.
    """
    try:
        return service.obtener_items_rojos(id_empresa)
    except Exception as e:
        logger.error(f"Error al obtener items rojos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/semaforo/amarillo",
    response_model=List[InsumoSemaforo],
    summary="Items en estado amarillo (atención)"
)
def obtener_items_amarillos(
    id_empresa: int = Query(default=1, description="ID de la empresa"),
    service: AlertasService = Depends(get_alertas_service)
):
    """
    Obtiene solo los items en estado amarillo (vencen en 7-15 días).
    Estos deben usarse esta semana.
    """
    try:
        return service.obtener_items_amarillos(id_empresa)
    except Exception as e:
        logger.error(f"Error al obtener items amarillos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STOCK CRÍTICO ====================

@router.get(
    "/stock-critico",
    response_model=ResumenStockCritico,
    summary="Insumos con stock crítico"
)
def obtener_stock_critico(service: AlertasService = Depends(get_alertas_service)):
    """
    Obtiene lista de insumos cuyo stock actual está por debajo del mínimo.
    Incluye insumos sin stock (es_critico=true) y con stock bajo.
    """
    try:
        return service.obtener_stock_critico()
    except Exception as e:
        logger.error(f"Error al obtener stock crítico: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== USAR HOY (FEFO) ====================

@router.get(
    "/usar-hoy",
    response_model=ListaUsarHoy,
    summary="Lista FEFO de items a usar hoy"
)
def obtener_usar_hoy(
    id_empresa: int = Query(default=1, description="ID de la empresa"),
    service: AlertasService = Depends(get_alertas_service)
):
    """
    Genera lista FEFO (First Expired, First Out) de items que deben usarse hoy.
    Prioriza los que vencen primero.
    """
    try:
        return service.obtener_lista_usar_hoy(id_empresa)
    except Exception as e:
        logger.error(f"Error al obtener lista usar hoy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== EJECUCIÓN MANUAL DEL JOB ====================

@router.post(
    "/ejecutar-job",
    response_model=JobEjecutarResponse,
    summary="Ejecutar job de alertas manualmente"
)
def ejecutar_job_manual(
    id_empresa: int = Query(default=1, description="ID de la empresa"),
    db: Session = Depends(get_db)
):
    """
    Ejecuta manualmente el job de generación de alertas.
    Útil para testing o ejecución bajo demanda.
    """
    from jobs.alertas_job import ejecutar_alertas_diarias
    
    try:
        start_time = time.time()
        
        resultado = ejecutar_alertas_diarias(db, id_empresa)
        
        tiempo_ms = int((time.time() - start_time) * 1000)
        
        return JobEjecutarResponse(
            success=True,
            message="Job ejecutado exitosamente",
            alertas_vencimiento_creadas=resultado.get("alertas_vencimiento", 0),
            alertas_stock_creadas=resultado.get("alertas_stock", 0),
            emails_encolados=resultado.get("emails_encolados", 0),
            tiempo_ejecucion_ms=tiempo_ms
        )
    except Exception as e:
        logger.error(f"Error al ejecutar job manualmente: {e}")
        raise HTTPException(status_code=500, detail=str(e))
