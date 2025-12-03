"""
Interface del repositorio de Promociones.
Define el contrato para operaciones de base de datos del módulo de promociones.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .model import Promocion, EstadoPromocion


class PromocionRepositoryInterface(ABC):
    """Interface para el repositorio de promociones."""

    @abstractmethod
    def get_all(self, include_anulados: bool = False) -> List[Promocion]:
        """Obtiene todas las promociones."""
        pass

    @abstractmethod
    def get_by_id(self, promocion_id: int) -> Optional[Promocion]:
        """Obtiene una promoción por su ID."""
        pass

    @abstractmethod
    def get_by_codigo(self, codigo: str) -> Optional[Promocion]:
        """Obtiene una promoción por su código."""
        pass

    @abstractmethod
    def get_activas(self) -> List[Promocion]:
        """Obtiene promociones activas."""
        pass

    @abstractmethod
    def get_sugeridas(self) -> List[Promocion]:
        """Obtiene promociones sugeridas."""
        pass

    @abstractmethod
    def get_by_producto(self, producto_id: int) -> List[Promocion]:
        """Obtiene promociones de un producto."""
        pass

    @abstractmethod
    def get_by_estado(self, estado: EstadoPromocion) -> List[Promocion]:
        """Obtiene promociones por estado."""
        pass

    @abstractmethod
    def create(self, promocion_data: dict, productos_combo: List[dict] = None) -> Promocion:
        """Crea una nueva promoción."""
        pass

    @abstractmethod
    def update(self, promocion_id: int, update_data: dict, productos_combo: List[dict] = None) -> Optional[Promocion]:
        """Actualiza una promoción existente."""
        pass

    @abstractmethod
    def cambiar_estado(self, promocion_id: int, nuevo_estado: EstadoPromocion) -> Optional[Promocion]:
        """Cambia el estado de una promoción."""
        pass

    @abstractmethod
    def incrementar_uso(self, promocion_id: int) -> Optional[Promocion]:
        """Incrementa el contador de uso de una promoción."""
        pass

    @abstractmethod
    def delete(self, promocion_id: int) -> bool:
        """Elimina (soft delete) una promoción."""
        pass

    @abstractmethod
    def delete_sugerencias_producto(self, producto_id: int) -> int:
        """Elimina todas las sugerencias automáticas de un producto."""
        pass

    @abstractmethod
    def get_next_codigo(self) -> str:
        """Genera el siguiente código de promoción."""
        pass
