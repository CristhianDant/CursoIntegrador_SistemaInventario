"""
Interface del servicio de Alertas.
Define el contrato para la lógica de negocio del módulo de alertas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .schemas import (
    NotificacionResponse,
    ResumenSemaforo,
    ResumenStockCritico,
    ListaUsarHoy,
    ResumenAlertas,
    InsumoSemaforo
)


class AlertasServiceInterface(ABC):
    """Interface para el servicio de alertas."""

    # ==================== CONFIGURACIÓN ====================

    @abstractmethod
    def obtener_configuracion_alertas(self, id_empresa: int = 1) -> dict:
        """Obtiene la configuración de alertas de la empresa."""
        pass

    @abstractmethod
    def actualizar_configuracion_alertas(
        self,
        id_empresa: int,
        configuracion: dict
    ) -> dict:
        """Actualiza la configuración de alertas de la empresa."""
        pass

    # ==================== NOTIFICACIONES ====================

    @abstractmethod
    def obtener_notificaciones(
        self,
        tipo: Optional[str] = None,
        solo_no_leidas: bool = False,
        limit: int = 100
    ) -> List[NotificacionResponse]:
        """Obtiene lista de notificaciones con filtros."""
        pass

    @abstractmethod
    def marcar_notificacion_leida(self, id_notificacion: int) -> bool:
        """Marca una notificación como leída."""
        pass

    @abstractmethod
    def marcar_todas_leidas(self, tipo: Optional[str] = None) -> int:
        """Marca todas las notificaciones como leídas."""
        pass

    @abstractmethod
    def obtener_resumen_alertas(self) -> ResumenAlertas:
        """Obtiene resumen de alertas activas."""
        pass

    # ==================== SEMÁFORO DE VENCIMIENTOS ====================

    @abstractmethod
    def obtener_semaforo_vencimientos(self, id_empresa: int = 1) -> ResumenSemaforo:
        """Obtiene el semáforo completo de vencimientos."""
        pass

    @abstractmethod
    def obtener_items_rojos(self, id_empresa: int = 1) -> List[InsumoSemaforo]:
        """Obtiene solo los items en estado rojo."""
        pass

    @abstractmethod
    def obtener_items_amarillos(self, id_empresa: int = 1) -> List[InsumoSemaforo]:
        """Obtiene solo los items en estado amarillo."""
        pass

    # ==================== STOCK CRÍTICO ====================

    @abstractmethod
    def obtener_stock_critico(self) -> ResumenStockCritico:
        """Obtiene resumen de insumos con stock crítico."""
        pass

    # ==================== USAR HOY (FEFO) ====================

    @abstractmethod
    def obtener_lista_usar_hoy(self, id_empresa: int = 1) -> ListaUsarHoy:
        """Obtiene lista FEFO de items a usar hoy."""
        pass
