"""
Interface del repositorio de Alertas.
Define el contrato para operaciones de base de datos del módulo de alertas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session

from .model import Notificacion, TipoAlerta


class AlertasRepositoryInterface(ABC):
    """Interface para el repositorio de alertas."""

    # ==================== NOTIFICACIONES CRUD ====================

    @abstractmethod
    def crear_notificacion(self, notificacion: Notificacion) -> Notificacion:
        """Crea una nueva notificación."""
        pass

    @abstractmethod
    def crear_notificaciones_batch(self, notificaciones: List[Notificacion]) -> int:
        """Crea múltiples notificaciones en batch."""
        pass

    @abstractmethod
    def obtener_notificacion_por_id(self, id_notificacion: int) -> Optional[Notificacion]:
        """Obtiene una notificación por su ID."""
        pass

    @abstractmethod
    def obtener_notificaciones_activas(
        self,
        tipo: Optional[TipoAlerta] = None,
        solo_no_leidas: bool = False,
        limit: int = 100
    ) -> List[Notificacion]:
        """Obtiene notificaciones activas con filtros opcionales."""
        pass

    @abstractmethod
    def marcar_como_leida(self, id_notificacion: int) -> bool:
        """Marca una notificación como leída."""
        pass

    @abstractmethod
    def marcar_todas_como_leidas(self, tipo: Optional[TipoAlerta] = None) -> int:
        """Marca todas las notificaciones como leídas."""
        pass

    @abstractmethod
    def desactivar_notificaciones_antiguas_por_insumo(
        self,
        id_insumo: int,
        tipo: TipoAlerta
    ) -> int:
        """Desactiva notificaciones anteriores del mismo tipo para un insumo."""
        pass

    @abstractmethod
    def contar_no_leidas_por_tipo(self) -> dict:
        """Cuenta notificaciones no leídas agrupadas por tipo."""
        pass

    # ==================== CONSULTAS SQL ====================

    @abstractmethod
    def obtener_lotes_por_vencer(self, dias_limite: int = 15) -> List[dict]:
        """Obtiene lotes que vencen en los próximos X días."""
        pass

    @abstractmethod
    def obtener_stock_por_insumo(self) -> List[dict]:
        """Obtiene el stock actual de cada insumo."""
        pass

    @abstractmethod
    def obtener_lista_usar_hoy(self, dias_rojo: int = 3) -> List[dict]:
        """Obtiene lista FEFO de insumos a usar hoy/pronto."""
        pass

    @abstractmethod
    def obtener_resumen_semaforo(
        self,
        dias_verde: int = 15,
        dias_amarillo: int = 7,
        dias_rojo: int = 3
    ) -> dict:
        """Obtiene conteo de lotes por estado de semáforo."""
        pass

    @abstractmethod
    def verificar_notificacion_existente(
        self,
        id_insumo: int,
        tipo: TipoAlerta,
        id_ingreso_detalle: Optional[int] = None
    ) -> bool:
        """Verifica si ya existe una notificación activa para evitar duplicados."""
        pass
