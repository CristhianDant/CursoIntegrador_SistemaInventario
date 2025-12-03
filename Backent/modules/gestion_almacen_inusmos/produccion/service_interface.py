"""
Interface del servicio de Producción.
Define el contrato para la lógica de negocio del módulo de producción.
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from decimal import Decimal

from .schemas import (
    ProduccionRequest,
    ValidacionStockResponse,
    ProduccionResponse,
    HistorialProduccionResponse,
    TrazabilidadProduccionResponse
)


class ProduccionServiceInterface(ABC):
    """Interface para el servicio de producción."""

    @abstractmethod
    def validar_stock_receta(
        self,
        db: Session,
        id_receta: int,
        cantidad_batch: Decimal
    ) -> ValidacionStockResponse:
        """Valida si hay stock suficiente para producir la cantidad de batch indicada."""
        pass

    @abstractmethod
    def ejecutar_produccion(
        self,
        db: Session,
        request: ProduccionRequest
    ) -> ProduccionResponse:
        """Ejecuta la producción descontando insumos en orden FEFO."""
        pass

    @abstractmethod
    def get_historial_producciones(
        self,
        db: Session,
        limit: int = 50,
        offset: int = 0
    ) -> HistorialProduccionResponse:
        """Obtiene el historial de producciones realizadas."""
        pass

    @abstractmethod
    def get_trazabilidad_produccion(
        self,
        db: Session,
        id_produccion: int
    ) -> TrazabilidadProduccionResponse:
        """Obtiene la trazabilidad completa de una producción."""
        pass
