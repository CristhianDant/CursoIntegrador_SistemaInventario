"""
Interface del servicio de Insumo.
Define el contrato para la lógica de negocio del módulo de insumos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from .schemas import Insumo, InsumoCreate, InsumoUpdate


class InsumoServiceInterface(ABC):
    """Interface para el servicio de insumos."""

    @abstractmethod
    def create_insumo(self, insumo: InsumoCreate) -> Insumo:
        """Crea un nuevo insumo."""
        pass

    @abstractmethod
    def get_insumos(self, skip: int = 0, limit: int = 100) -> List[Insumo]:
        """Obtiene lista de insumos con paginación."""
        pass

    @abstractmethod
    def get_insumo(self, insumo_id: int) -> Optional[Insumo]:
        """Obtiene un insumo por su ID."""
        pass

    @abstractmethod
    def update_insumo(self, insumo_id: int, insumo: InsumoUpdate) -> Optional[Insumo]:
        """Actualiza un insumo existente."""
        pass

    @abstractmethod
    def delete_insumo(self, insumo_id: int) -> Optional[Insumo]:
        """Elimina (soft delete) un insumo."""
        pass

    @abstractmethod
    def get_ultimos_precios(self) -> Dict[int, float]:
        """Obtiene el último precio de compra de cada insumo."""
        pass
