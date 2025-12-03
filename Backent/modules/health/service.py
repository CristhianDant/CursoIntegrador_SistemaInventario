"""
Servicio de Health Checks.

Implementa la lógica para verificar el estado de los componentes del sistema.
"""

import time
import platform
import psutil
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from loguru import logger

from .schemas import (
    HealthStatus,
    ComponentHealth,
    HealthResponse,
    ReadinessResponse,
    DetailedHealthResponse
)
from config import settings


class HealthService:
    """Servicio para verificar el estado de salud del sistema."""
    
    # Tiempo de inicio de la aplicación (se establece al importar)
    _start_time: float = time.time()
    _version: str = "1.0.0"
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    @classmethod
    def get_uptime_seconds(cls) -> float:
        """Obtiene el tiempo que lleva la aplicación corriendo."""
        return time.time() - cls._start_time
    
    @classmethod
    def set_version(cls, version: str):
        """Establece la versión de la aplicación."""
        cls._version = version
    
    # ==================== LIVENESS CHECK ====================
    
    def check_liveness(self) -> HealthResponse:
        """
        Verifica que la aplicación está viva.
        
        Este check debe ser rápido y no depender de servicios externos.
        Solo verifica que el proceso Python está corriendo.
        """
        return HealthResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            version=self._version,
            uptime_seconds=self.get_uptime_seconds()
        )
    
    # ==================== READINESS CHECK ====================
    
    def check_readiness(self) -> ReadinessResponse:
        """
        Verifica que la aplicación está lista para recibir tráfico.
        
        Comprueba todos los componentes críticos:
        - Base de datos
        - Scheduler
        - Servicios externos (SMTP)
        """
        components: List[ComponentHealth] = []
        
        # Verificar base de datos
        db_health = self._check_database()
        components.append(db_health)
        
        # Verificar scheduler
        scheduler_health = self._check_scheduler()
        components.append(scheduler_health)
        
        # Verificar SMTP (opcional, puede estar degradado)
        smtp_health = self._check_smtp()
        components.append(smtp_health)
        
        # Calcular estado general
        overall_status = self._calculate_overall_status(components)
        
        # Contar estados
        healthy = sum(1 for c in components if c.status == HealthStatus.HEALTHY)
        degraded = sum(1 for c in components if c.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for c in components if c.status == HealthStatus.UNHEALTHY)
        
        return ReadinessResponse(
            status=overall_status,
            timestamp=datetime.now(),
            version=self._version,
            uptime_seconds=self.get_uptime_seconds(),
            components=components,
            total_components=len(components),
            healthy_components=healthy,
            degraded_components=degraded,
            unhealthy_components=unhealthy
        )
    
    # ==================== DETAILED STATUS ====================
    
    def get_detailed_status(self) -> DetailedHealthResponse:
        """
        Obtiene el estado detallado del sistema.
        
        Incluye métricas del sistema, información del scheduler y estadísticas de BD.
        """
        # Primero obtener readiness
        readiness = self.check_readiness()
        
        # Obtener información del sistema
        system_info = self._get_system_info()
        
        # Obtener información del scheduler
        scheduler_info = self._get_scheduler_info()
        
        # Obtener estadísticas de la base de datos
        database_stats = self._get_database_stats()
        
        return DetailedHealthResponse(
            status=readiness.status,
            timestamp=datetime.now(),
            version=self._version,
            uptime_seconds=self.get_uptime_seconds(),
            components=readiness.components,
            system_info=system_info,
            scheduler_info=scheduler_info,
            database_stats=database_stats
        )
    
    # ==================== COMPONENTES INDIVIDUALES ====================
    
    def _check_database(self) -> ComponentHealth:
        """Verifica la conexión a la base de datos."""
        start_time = time.time()
        
        try:
            if self.db is None:
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.UNHEALTHY,
                    message="No database session available"
                )
            
            # Ejecutar query simple para verificar conexión
            self.db.execute(text("SELECT 1"))
            response_time = (time.time() - start_time) * 1000
            
            # Determinar estado basado en tiempo de respuesta
            if response_time < 100:
                status = HealthStatus.HEALTHY
                message = "Database connection is healthy"
            elif response_time < 500:
                status = HealthStatus.DEGRADED
                message = f"Database responding slowly ({response_time:.0f}ms)"
            else:
                status = HealthStatus.DEGRADED
                message = f"Database very slow ({response_time:.0f}ms)"
            
            return ComponentHealth(
                name="database",
                status=status,
                response_time_ms=round(response_time, 2),
                message=message,
                details={
                    "host": settings.HOST_DB,
                    "database": settings.POST_DB
                }
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Database health check failed: {e}")
            
            return ComponentHealth(
                name="database",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=round(response_time, 2),
                message=f"Database connection failed: {str(e)}"
            )
    
    def _check_scheduler(self) -> ComponentHealth:
        """Verifica el estado del scheduler."""
        try:
            from core.scheduler import scheduler, get_scheduler_status
            
            status_info = get_scheduler_status()
            
            if not settings.SCHEDULER_ENABLED:
                return ComponentHealth(
                    name="scheduler",
                    status=HealthStatus.DEGRADED,
                    message="Scheduler is disabled in configuration",
                    details=status_info
                )
            
            if status_info.get("running", False):
                jobs_count = len(status_info.get("jobs", []))
                return ComponentHealth(
                    name="scheduler",
                    status=HealthStatus.HEALTHY,
                    message=f"Scheduler running with {jobs_count} jobs",
                    details=status_info
                )
            else:
                return ComponentHealth(
                    name="scheduler",
                    status=HealthStatus.UNHEALTHY,
                    message="Scheduler is not running",
                    details=status_info
                )
                
        except Exception as e:
            logger.error(f"Scheduler health check failed: {e}")
            return ComponentHealth(
                name="scheduler",
                status=HealthStatus.UNHEALTHY,
                message=f"Scheduler check failed: {str(e)}"
            )
    
    def _check_smtp(self) -> ComponentHealth:
        """Verifica la configuración SMTP (sin enviar email)."""
        try:
            # Solo verificar que la configuración existe
            if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
                return ComponentHealth(
                    name="smtp",
                    status=HealthStatus.DEGRADED,
                    message="SMTP credentials not configured",
                    details={
                        "host": settings.SMTP_HOST,
                        "port": settings.SMTP_PORT,
                        "configured": False
                    }
                )
            
            return ComponentHealth(
                name="smtp",
                status=HealthStatus.HEALTHY,
                message="SMTP configured",
                details={
                    "host": settings.SMTP_HOST,
                    "port": settings.SMTP_PORT,
                    "configured": True
                }
            )
            
        except Exception as e:
            return ComponentHealth(
                name="smtp",
                status=HealthStatus.DEGRADED,
                message=f"SMTP check failed: {str(e)}"
            )
    
    # ==================== UTILIDADES ====================
    
    def _calculate_overall_status(self, components: List[ComponentHealth]) -> HealthStatus:
        """Calcula el estado general basado en los componentes."""
        # Si cualquier componente crítico está unhealthy, el sistema está unhealthy
        critical_components = ["database"]
        
        for comp in components:
            if comp.name in critical_components and comp.status == HealthStatus.UNHEALTHY:
                return HealthStatus.UNHEALTHY
        
        # Si hay algún unhealthy no crítico o degraded, el sistema está degraded
        for comp in components:
            if comp.status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]:
                return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def _get_system_info(self) -> dict:
        """Obtiene información del sistema."""
        try:
            return {
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory": {
                    "total_mb": round(psutil.virtual_memory().total / (1024 * 1024), 2),
                    "available_mb": round(psutil.virtual_memory().available / (1024 * 1024), 2),
                    "percent_used": psutil.virtual_memory().percent
                },
                "disk": {
                    "total_gb": round(psutil.disk_usage('/').total / (1024 * 1024 * 1024), 2),
                    "free_gb": round(psutil.disk_usage('/').free / (1024 * 1024 * 1024), 2),
                    "percent_used": psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            logger.warning(f"Could not get system info: {e}")
            return {"error": str(e)}
    
    def _get_scheduler_info(self) -> dict:
        """Obtiene información detallada del scheduler."""
        try:
            from core.scheduler import get_scheduler_status
            return get_scheduler_status()
        except Exception as e:
            return {"error": str(e)}
    
    def _get_database_stats(self) -> dict:
        """Obtiene estadísticas de la base de datos."""
        try:
            if self.db is None:
                return {"error": "No database session"}
            
            # Contar registros de tablas principales
            from modules.insumo.model import Insumo
            from modules.productos_terminados.model import ProductoTerminado
            from modules.alertas.model import Notificacion
            
            insumos_count = self.db.query(Insumo).count()
            productos_count = self.db.query(ProductoTerminado).count()
            alertas_count = self.db.query(Notificacion).filter(
                Notificacion.activa == True
            ).count()
            
            return {
                "insumos_count": insumos_count,
                "productos_count": productos_count,
                "alertas_activas": alertas_count
            }
            
        except Exception as e:
            logger.warning(f"Could not get database stats: {e}")
            return {"error": str(e)}
