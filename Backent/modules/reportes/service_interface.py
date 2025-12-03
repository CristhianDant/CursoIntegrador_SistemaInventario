"""
Interface del servicio de Reportes.
Define el contrato para la lógica de negocio del módulo de reportes.
"""

from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

from .schemas import (
    ReporteABCResponse,
    ReporteDiarioResponse,
    KPIsResponse,
    RotacionResponse
)


class ReportesServiceInterface(ABC):
    """Interface para el servicio de reportes."""

    # ==================== ANÁLISIS ABC ====================

    @abstractmethod
    def generar_reporte_abc(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        categoria: Optional[str] = None
    ) -> ReporteABCResponse:
        """Genera análisis ABC de productos por ventas."""
        pass

    # ==================== REPORTE DIARIO ====================

    @abstractmethod
    def generar_reporte_diario(self, fecha: Optional[date] = None) -> ReporteDiarioResponse:
        """Genera el reporte diario completo."""
        pass

    # ==================== KPIs ====================

    @abstractmethod
    def obtener_kpis(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> KPIsResponse:
        """Obtiene KPIs del período."""
        pass

    # ==================== ROTACIÓN ====================

    @abstractmethod
    def generar_reporte_rotacion(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        limite: int = 50
    ) -> RotacionResponse:
        """Genera reporte de rotación de inventario."""
        pass
