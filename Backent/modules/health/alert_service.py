"""
Servicio de Alertas de Salud del Sistema.

Monitorea el estado de los componentes y genera alertas cuando
hay degradación o fallos en el sistema.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger

from config import settings
from modules.health.service import HealthService
from modules.health.schemas import HealthStatus, ComponentHealth
from database import SessionLocal


class SystemHealthAlertService:
    """
    Servicio para monitorear la salud del sistema y generar alertas.
    
    Funcionalidades:
    - Verificar periódicamente el estado del sistema
    - Crear notificaciones cuando hay problemas
    - Enviar emails para alertas críticas
    - Mantener historial de estados
    """
    
    # Historial de estados para detectar cambios
    _last_status: dict = {}
    _last_check: Optional[datetime] = None
    _consecutive_failures: dict = {}
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    def check_and_alert(self) -> dict:
        """
        Verifica el estado del sistema y genera alertas si hay problemas.
        
        Returns:
            Diccionario con resumen de la verificación
        """
        if not settings.HEALTH_CHECK_ALERT_ENABLED:
            return {"enabled": False, "message": "Health alerts disabled"}
        
        health_service = HealthService(self.db)
        readiness = health_service.check_readiness()
        
        alerts_created = []
        
        for component in readiness.components:
            alert = self._evaluate_component(component)
            if alert:
                alerts_created.append(alert)
        
        self.__class__._last_check = datetime.now()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": readiness.status.value,
            "components_checked": len(readiness.components),
            "alerts_created": len(alerts_created),
            "alerts": alerts_created
        }
    
    def _evaluate_component(self, component: ComponentHealth) -> Optional[dict]:
        """
        Evalúa un componente y decide si generar alerta.
        
        Lógica:
        - Si el estado cambió a peor, generar alerta
        - Si hay fallos consecutivos, escalar alerta
        - Si se recuperó, generar alerta de recuperación
        """
        component_name = component.name
        current_status = component.status
        
        # Obtener estado anterior
        previous_status = self._last_status.get(component_name)
        
        # Actualizar estado actual
        self.__class__._last_status[component_name] = current_status
        
        alert = None
        
        # Caso 1: Componente pasó a UNHEALTHY
        if current_status == HealthStatus.UNHEALTHY:
            # Incrementar contador de fallos
            failures = self._consecutive_failures.get(component_name, 0) + 1
            self.__class__._consecutive_failures[component_name] = failures
            
            alert = self._create_alert(
                component=component,
                alert_type="SYSTEM_UNHEALTHY",
                severity="CRITICAL" if failures >= 3 else "HIGH",
                message=f"Componente {component_name} está UNHEALTHY: {component.message}",
                consecutive_failures=failures
            )
            
            # Log con contexto de health check
            logger.bind(health_check=True, system_alert=True).error(
                f"🔴 ALERTA CRÍTICA: {component_name} - {component.message}"
            )
        
        # Caso 2: Componente pasó a DEGRADED
        elif current_status == HealthStatus.DEGRADED:
            # Solo alertar si cambió de HEALTHY a DEGRADED
            if previous_status == HealthStatus.HEALTHY:
                alert = self._create_alert(
                    component=component,
                    alert_type="SYSTEM_DEGRADED",
                    severity="MEDIUM",
                    message=f"Componente {component_name} está DEGRADED: {component.message}"
                )
                
                logger.bind(health_check=True, system_alert=True).warning(
                    f"🟡 ALERTA: {component_name} degradado - {component.message}"
                )
        
        # Caso 3: Componente se recuperó
        elif current_status == HealthStatus.HEALTHY:
            # Reset contador de fallos
            if component_name in self._consecutive_failures:
                del self.__class__._consecutive_failures[component_name]
            
            # Notificar recuperación si antes estaba mal
            if previous_status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]:
                alert = self._create_alert(
                    component=component,
                    alert_type="SYSTEM_RECOVERED",
                    severity="INFO",
                    message=f"Componente {component_name} se ha recuperado"
                )
                
                logger.bind(health_check=True, system_alert=True).info(
                    f"🟢 RECUPERADO: {component_name} volvió a estado healthy"
                )
        
        return alert
    
    def _create_alert(
        self,
        component: ComponentHealth,
        alert_type: str,
        severity: str,
        message: str,
        consecutive_failures: int = 0
    ) -> dict:
        """
        Crea una alerta de salud del sistema.
        
        Si hay base de datos disponible, la guarda como notificación.
        """
        alert_data = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "severity": severity,
            "component": component.name,
            "status": component.status.value,
            "message": message,
            "details": component.details,
            "response_time_ms": component.response_time_ms,
            "consecutive_failures": consecutive_failures
        }
        
        # Intentar guardar en base de datos si está disponible
        if self.db and alert_type != "SYSTEM_RECOVERED":
            try:
                self._save_notification(alert_data)
            except Exception as e:
                logger.warning(f"No se pudo guardar alerta en BD: {e}")
        
        # Enviar email para alertas críticas
        if severity == "CRITICAL" and consecutive_failures >= 3:
            self._send_critical_email(alert_data)
        
        return alert_data
    
    def _save_notification(self, alert_data: dict):
        """Guarda la alerta como notificación en la base de datos."""
        from modules.alertas.model import Notificacion, TipoAlerta
        
        # Mapear tipo de alerta del sistema a tipo de alerta existente
        # Usamos STOCK_CRITICO como el tipo más apropiado para alertas de sistema
        # En producción, se debería agregar un nuevo tipo SYSTEM_HEALTH
        
        notificacion = Notificacion(
            tipo=TipoAlerta.STOCK_CRITICO,  # TODO: Agregar TipoAlerta.SYSTEM_HEALTH
            titulo=f"⚠️ Alerta de Sistema: {alert_data['component']}",
            mensaje=alert_data['message'],
            semaforo=None,
            dias_restantes=None,
            cantidad_afectada=str(alert_data.get('consecutive_failures', 0)),
            leida=False,
            activa=True
        )
        
        self.db.add(notificacion)
        self.db.commit()
        
        logger.info(f"Notificación de sistema guardada: {notificacion.id_notificacion}")
    
    def _send_critical_email(self, alert_data: dict):
        """Envía email para alertas críticas."""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP no configurado, no se puede enviar email de alerta")
            return
        
        try:
            from modules.email_service.service import EmailService
            
            email_service = EmailService()
            
            subject = f"🚨 ALERTA CRÍTICA: {alert_data['component']} - Sistema de Inventario"
            
            body = f"""
            <h2>⚠️ Alerta Crítica del Sistema</h2>
            
            <p><strong>Componente:</strong> {alert_data['component']}</p>
            <p><strong>Estado:</strong> {alert_data['status']}</p>
            <p><strong>Mensaje:</strong> {alert_data['message']}</p>
            <p><strong>Fallos consecutivos:</strong> {alert_data['consecutive_failures']}</p>
            <p><strong>Timestamp:</strong> {alert_data['timestamp']}</p>
            
            <hr>
            <p>Este es un mensaje automático del Sistema de Inventario.</p>
            <p>Por favor, verifique el estado del sistema inmediatamente.</p>
            """
            
            # Enviar a administrador (usar SMTP_USER como destinatario por defecto)
            email_service.send_email(
                to_email=settings.SMTP_USER,
                subject=subject,
                body=body,
                is_html=True
            )
            
            logger.info(f"Email de alerta crítica enviado a {settings.SMTP_USER}")
            
        except Exception as e:
            logger.error(f"Error enviando email de alerta: {e}")


# ==================== FUNCIONES DE UTILIDAD ====================

def run_health_check():
    """
    Ejecuta verificación de salud (para uso en jobs programados).
    """
    db = SessionLocal()
    try:
        service = SystemHealthAlertService(db)
        result = service.check_and_alert()
        logger.info(f"Health check completado: {result}")
        return result
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {"error": str(e)}
    finally:
        db.close()


async def periodic_health_check():
    """
    Ejecuta verificaciones de salud periódicamente.
    
    Para usar con asyncio en background.
    """
    interval = settings.HEALTH_CHECK_INTERVAL_SECONDS
    
    while True:
        try:
            result = run_health_check()
            if result.get("alerts_created", 0) > 0:
                logger.warning(f"Health check generó {result['alerts_created']} alertas")
        except Exception as e:
            logger.error(f"Error en periodic health check: {e}")
        
        await asyncio.sleep(interval)
