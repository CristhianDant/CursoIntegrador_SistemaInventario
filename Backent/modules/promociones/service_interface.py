"""
Interface del servicio de Promociones.
Define el contrato para la lógica de negocio del módulo de promociones.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .schemas import (
    PromocionCreate, 
    PromocionUpdate, 
    PromocionResponse, 
    SugerenciaPromocion, 
    EstadisticasPromociones
)


class PromocionServiceInterface(ABC):
    """Interface para el servicio de promociones."""

    @abstractmethod
    def get_all(self) -> List[PromocionResponse]:
        """Obtiene todas las promociones."""
        pass

    @abstractmethod
    def get_by_id(self, promocion_id: int) -> Optional[PromocionResponse]:
        """Obtiene una promoción por su ID."""
        pass

    @abstractmethod
    def get_activas(self) -> List[PromocionResponse]:
        """Obtiene promociones activas."""
        pass

    @abstractmethod
    def get_sugeridas(self) -> List[PromocionResponse]:
        """Obtiene promociones sugeridas."""
        pass

    @abstractmethod
    def create(self, data: PromocionCreate) -> PromocionResponse:
        """Crea una nueva promoción."""
        pass

    @abstractmethod
    def update(self, promocion_id: int, data: PromocionUpdate) -> Optional[PromocionResponse]:
        """Actualiza una promoción existente."""
        pass

    @abstractmethod
    def activar(self, promocion_id: int) -> Optional[PromocionResponse]:
        """Activa una promoción."""
        pass

    @abstractmethod
    def pausar(self, promocion_id: int) -> Optional[PromocionResponse]:
        """Pausa una promoción."""
        pass

    @abstractmethod
    def cancelar(self, promocion_id: int) -> Optional[PromocionResponse]:
        """Cancela una promoción."""
        pass

    @abstractmethod
    def finalizar(self, promocion_id: int) -> Optional[PromocionResponse]:
        """Finaliza una promoción."""
        pass

    @abstractmethod
    def delete(self, promocion_id: int) -> bool:
        """Elimina (soft delete) una promoción."""
        pass

    @abstractmethod
    def generar_sugerencias(self, dias_alerta: int = 7) -> List[SugerenciaPromocion]:
        """Genera sugerencias de promociones basadas en productos por vencer."""
        pass
