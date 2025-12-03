"""
Schemas para el módulo de Health Checks.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class HealthStatus(str, Enum):
    """Estados posibles de salud de un componente."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComponentHealth(BaseModel):
    """Estado de salud de un componente individual."""
    name: str
    status: HealthStatus
    response_time_ms: Optional[float] = None
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """
    Respuesta del endpoint /health (Liveness Probe).
    
    Indica si la aplicación está viva y puede recibir tráfico.
    """
    status: HealthStatus
    timestamp: datetime
    version: str
    uptime_seconds: float

    model_config = ConfigDict(from_attributes=True)


class ReadinessResponse(BaseModel):
    """
    Respuesta del endpoint /ready (Readiness Probe).
    
    Indica si la aplicación está lista para procesar requests.
    Verifica todos los componentes críticos.
    """
    status: HealthStatus
    timestamp: datetime
    version: str
    uptime_seconds: float
    components: List[ComponentHealth]
    
    # Resumen
    total_components: int
    healthy_components: int
    degraded_components: int
    unhealthy_components: int

    model_config = ConfigDict(from_attributes=True)


class DetailedHealthResponse(BaseModel):
    """
    Respuesta detallada del endpoint /status.
    
    Incluye métricas adicionales del sistema.
    """
    status: HealthStatus
    timestamp: datetime
    version: str
    uptime_seconds: float
    components: List[ComponentHealth]
    
    # Métricas del sistema
    system_info: Dict[str, Any]
    
    # Información del scheduler
    scheduler_info: Optional[Dict[str, Any]] = None
    
    # Estadísticas de la BD
    database_stats: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class HealthAlertCreate(BaseModel):
    """Schema para crear una alerta de salud del sistema."""
    component: str
    status: HealthStatus
    message: str
    details: Optional[Dict[str, Any]] = None
