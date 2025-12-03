"""
Tests para el módulo de Health Checks.

Prueba los endpoints de monitoreo y el servicio de health checks.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from modules.health.service import HealthService
from modules.health.schemas import HealthStatus, HealthResponse, ReadinessResponse


class TestHealthService:
    """Tests para HealthService."""
    
    def test_check_liveness_returns_healthy(self):
        """Test que liveness check retorna healthy."""
        service = HealthService()
        
        result = service.check_liveness()
        
        assert result.status == HealthStatus.HEALTHY
        assert result.version == "1.0.0"
        assert result.uptime_seconds >= 0
        assert isinstance(result.timestamp, datetime)
    
    def test_get_uptime_returns_positive(self):
        """Test que uptime retorna valor positivo."""
        uptime = HealthService.get_uptime_seconds()
        
        assert uptime >= 0
        assert isinstance(uptime, float)
    
    def test_set_version_updates_version(self):
        """Test que set_version actualiza la versión."""
        original_version = HealthService._version
        
        HealthService.set_version("2.0.0")
        service = HealthService()
        result = service.check_liveness()
        
        assert result.version == "2.0.0"
        
        # Restaurar versión original
        HealthService.set_version(original_version)
    
    def test_check_readiness_without_db(self):
        """Test readiness sin base de datos."""
        service = HealthService(db=None)
        
        result = service.check_readiness()
        
        # Sin DB, debería tener al menos un componente unhealthy
        assert isinstance(result, ReadinessResponse)
        assert result.total_components >= 1
    
    def test_check_readiness_with_mock_db(self):
        """Test readiness con base de datos mock."""
        mock_db = Mock()
        mock_db.execute.return_value = None
        
        service = HealthService(db=mock_db)
        
        result = service.check_readiness()
        
        assert isinstance(result, ReadinessResponse)
        assert result.timestamp is not None
        
        # Verificar que se llamó a la DB
        mock_db.execute.assert_called()
    
    def test_calculate_overall_status_all_healthy(self):
        """Test cálculo de estado cuando todo está healthy."""
        from modules.health.schemas import ComponentHealth
        
        components = [
            ComponentHealth(name="database", status=HealthStatus.HEALTHY),
            ComponentHealth(name="scheduler", status=HealthStatus.HEALTHY),
            ComponentHealth(name="smtp", status=HealthStatus.HEALTHY),
        ]
        
        service = HealthService()
        result = service._calculate_overall_status(components)
        
        assert result == HealthStatus.HEALTHY
    
    def test_calculate_overall_status_database_unhealthy(self):
        """Test que database unhealthy hace todo unhealthy."""
        from modules.health.schemas import ComponentHealth
        
        components = [
            ComponentHealth(name="database", status=HealthStatus.UNHEALTHY),
            ComponentHealth(name="scheduler", status=HealthStatus.HEALTHY),
        ]
        
        service = HealthService()
        result = service._calculate_overall_status(components)
        
        assert result == HealthStatus.UNHEALTHY
    
    def test_calculate_overall_status_with_degraded(self):
        """Test que componente degraded hace todo degraded."""
        from modules.health.schemas import ComponentHealth
        
        components = [
            ComponentHealth(name="database", status=HealthStatus.HEALTHY),
            ComponentHealth(name="smtp", status=HealthStatus.DEGRADED),
        ]
        
        service = HealthService()
        result = service._calculate_overall_status(components)
        
        assert result == HealthStatus.DEGRADED


class TestHealthSchemas:
    """Tests para los schemas de Health."""
    
    def test_health_response_creation(self):
        """Test creación de HealthResponse."""
        response = HealthResponse(
            status=HealthStatus.HEALTHY,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=100.5
        )
        
        assert response.status == HealthStatus.HEALTHY
        assert response.version == "1.0.0"
        assert response.uptime_seconds == 100.5
    
    def test_readiness_response_counts(self):
        """Test que ReadinessResponse calcula conteos correctamente."""
        from modules.health.schemas import ComponentHealth
        
        response = ReadinessResponse(
            status=HealthStatus.DEGRADED,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=100.0,
            components=[
                ComponentHealth(name="db", status=HealthStatus.HEALTHY),
                ComponentHealth(name="smtp", status=HealthStatus.DEGRADED),
            ],
            total_components=2,
            healthy_components=1,
            degraded_components=1,
            unhealthy_components=0
        )
        
        assert response.total_components == 2
        assert response.healthy_components == 1
        assert response.degraded_components == 1


class TestHealthAlertService:
    """Tests para SystemHealthAlertService."""
    
    def test_check_and_alert_disabled(self):
        """Test que check_and_alert respeta configuración deshabilitada."""
        from modules.health.alert_service import SystemHealthAlertService
        
        with patch('modules.health.alert_service.settings') as mock_settings:
            mock_settings.HEALTH_CHECK_ALERT_ENABLED = False
            
            service = SystemHealthAlertService()
            result = service.check_and_alert()
            
            assert result["enabled"] == False
    
    def test_evaluate_component_unhealthy(self):
        """Test evaluación de componente unhealthy."""
        from modules.health.alert_service import SystemHealthAlertService
        from modules.health.schemas import ComponentHealth
        
        service = SystemHealthAlertService()
        
        # Limpiar estado previo
        SystemHealthAlertService._last_status = {}
        SystemHealthAlertService._consecutive_failures = {}
        
        component = ComponentHealth(
            name="test_component",
            status=HealthStatus.UNHEALTHY,
            message="Test failure"
        )
        
        alert = service._evaluate_component(component)
        
        assert alert is not None
        assert alert["type"] == "SYSTEM_UNHEALTHY"
        assert alert["severity"] in ["HIGH", "CRITICAL"]
    
    def test_evaluate_component_recovery(self):
        """Test detección de recuperación de componente."""
        from modules.health.alert_service import SystemHealthAlertService
        from modules.health.schemas import ComponentHealth
        
        service = SystemHealthAlertService()
        
        # Simular estado previo UNHEALTHY
        SystemHealthAlertService._last_status = {"test_comp": HealthStatus.UNHEALTHY}
        SystemHealthAlertService._consecutive_failures = {"test_comp": 2}
        
        component = ComponentHealth(
            name="test_comp",
            status=HealthStatus.HEALTHY,
            message="Recovered"
        )
        
        alert = service._evaluate_component(component)
        
        assert alert is not None
        assert alert["type"] == "SYSTEM_RECOVERED"
        assert alert["severity"] == "INFO"
        
        # Limpiar
        SystemHealthAlertService._last_status = {}
        SystemHealthAlertService._consecutive_failures = {}


class TestMiddlewareRequestID:
    """Tests para el middleware de Request ID."""
    
    def test_get_request_id_default(self):
        """Test que get_request_id retorna cadena vacía por defecto."""
        from middleware.request_id import get_request_id
        
        result = get_request_id()
        
        assert result == ""
    
    def test_request_id_context_var(self):
        """Test que el context var funciona correctamente."""
        from middleware.request_id import request_id_ctx, get_request_id
        
        # Establecer un request ID
        token = request_id_ctx.set("test-request-id")
        
        assert get_request_id() == "test-request-id"
        
        # Restaurar
        request_id_ctx.reset(token)
        assert get_request_id() == ""
