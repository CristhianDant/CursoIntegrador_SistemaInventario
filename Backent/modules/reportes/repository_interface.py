"""
Interface del repositorio de Reportes.
Define el contrato para consultas SQL de reportes.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal


class ReportesRepositoryInterface(ABC):
    """Interface para el repositorio de reportes."""

    # ==================== ANÁLISIS ABC ====================

    @abstractmethod
    def obtener_ventas_por_producto(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        categoria: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obtiene ventas agrupadas por producto para análisis ABC."""
        pass

    # ==================== REPORTE DIARIO ====================

    @abstractmethod
    def obtener_resumen_ventas_dia(self, fecha: date) -> Dict[str, Any]:
        """Obtiene resumen de ventas del día."""
        pass

    @abstractmethod
    def obtener_resumen_mermas_dia(self, fecha: date) -> Dict[str, Any]:
        """Obtiene resumen de mermas del día."""
        pass

    @abstractmethod
    def obtener_resumen_produccion_dia(self, fecha: date) -> Dict[str, Any]:
        """Obtiene resumen de producción del día."""
        pass

    # ==================== KPIs ====================

    @abstractmethod
    def obtener_tasa_merma_periodo(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Decimal:
        """Calcula la tasa de merma del período."""
        pass

    @abstractmethod
    def obtener_rotacion_inventario(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Decimal:
        """Calcula la rotación de inventario del período."""
        pass

    @abstractmethod
    def obtener_valor_inventario_actual(self) -> Decimal:
        """Obtiene el valor total del inventario actual."""
        pass

    # ==================== ROTACIÓN ====================

    @abstractmethod
    def obtener_rotacion_por_producto(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        limite: int = 50
    ) -> List[Dict[str, Any]]:
        """Obtiene la rotación de cada producto en el período."""
        pass

    @abstractmethod
    def obtener_productos_sin_movimiento(
        self,
        dias: int = 30
    ) -> List[Dict[str, Any]]:
        """Obtiene productos sin movimiento en los últimos X días."""
        pass
