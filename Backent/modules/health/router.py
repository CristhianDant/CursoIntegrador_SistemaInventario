"""
Router del módulo de Health Checks.

Endpoints para verificar el estado de la aplicación y sus componentes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from database import get_db
from .service import HealthService
from .alert_service import SystemHealthAlertService
from .schemas import (
    HealthResponse,
    ReadinessResponse,
    DetailedHealthResponse,
    HealthStatus
)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness Probe",
    description="""
    Verifica que la aplicación está viva y puede recibir tráfico.
    
    Este endpoint:
    - NO verifica servicios externos
    - Responde rápidamente (< 10ms)
    - Usado por Kubernetes/Docker para liveness probes
    
    **Usar para:** Verificar si el contenedor debe reiniciarse.
    """
)
async def liveness_check():
    """
    Endpoint de liveness - verifica que la app está corriendo.
    """
    service = HealthService()
    return service.check_liveness()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness Probe",
    description="""
    Verifica que la aplicación está lista para procesar requests.
    
    Este endpoint verifica:
    - ✅ Conexión a base de datos
    - ✅ Estado del scheduler
    - ✅ Configuración de servicios (SMTP)
    
    **Códigos de respuesta:**
    - 200: Sistema listo (healthy o degraded)
    - 503: Sistema no disponible (unhealthy)
    
    **Usar para:** Determinar si el servicio puede recibir tráfico.
    """
)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Endpoint de readiness - verifica conexión a DB y servicios.
    """
    service = HealthService(db)
    response = service.check_readiness()
    
    # Si está unhealthy, retornar 503
    if response.status == HealthStatus.UNHEALTHY:
        raise HTTPException(
            status_code=503,
            detail={
                "status": response.status.value,
                "message": "Service unavailable",
                "components": [c.model_dump() for c in response.components]
            }
        )
    
    return response


@router.get(
    "/status",
    response_model=DetailedHealthResponse,
    summary="Estado Detallado del Sistema",
    description="""
    Obtiene información detallada del estado del sistema.
    
    Incluye:
    - Estado de todos los componentes
    - Métricas del sistema (CPU, memoria, disco)
    - Información del scheduler y sus jobs
    - Estadísticas de la base de datos
    
    **Nota:** Este endpoint puede ser más lento que /health y /ready.
    Usar solo para diagnóstico, no para probes automáticos.
    """
)
async def detailed_status(db: Session = Depends(get_db)):
    """
    Endpoint de estado detallado con métricas del sistema.
    """
    service = HealthService(db)
    return service.get_detailed_status()


@router.post(
    "/health/check-and-alert",
    summary="Ejecutar verificación de salud con alertas",
    description="""
    Ejecuta una verificación de salud y genera alertas si hay problemas.
    
    Este endpoint:
    - Verifica todos los componentes
    - Compara con el estado anterior
    - Genera alertas si hay degradación
    - Envía emails para alertas críticas
    
    **Usar para:** Diagnóstico manual o integración con sistemas de monitoreo.
    """
)
async def check_and_alert(db: Session = Depends(get_db)):
    """
    Ejecuta health check y genera alertas si es necesario.
    """
    service = SystemHealthAlertService(db)
    return service.check_and_alert()


@router.get(
    "/ping",
    summary="Ping simple",
    description="Endpoint de ping mínimo para verificación rápida."
)
async def ping():
    """Ping simple sin procesamiento."""
    return {"ping": "pong"}
