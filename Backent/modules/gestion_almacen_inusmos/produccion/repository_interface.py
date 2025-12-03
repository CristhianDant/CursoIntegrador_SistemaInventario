"""
Interface del repositorio de Producción.
Define el contrato para operaciones de base de datos del módulo de producción.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo


class ProduccionRepositoryInterface(ABC):
    """Interface para el repositorio de producción."""

    @abstractmethod
    def get_receta_con_insumos(self, db: Session, id_receta: int) -> Optional[Dict[str, Any]]:
        """Obtiene la receta con sus insumos requeridos."""
        pass

    @abstractmethod
    def get_stock_disponible_insumo(self, db: Session, id_insumo: int) -> Decimal:
        """Obtiene el stock total disponible de un insumo."""
        pass

    @abstractmethod
    def get_lotes_fefo(self, db: Session, id_insumo: int) -> List[Dict[str, Any]]:
        """Obtiene los lotes de un insumo ordenados por FEFO."""
        pass

    @abstractmethod
    def descontar_lote(self, db: Session, id_ingreso_detalle: int, cantidad_a_descontar: Decimal) -> Decimal:
        """Descuenta cantidad de un lote específico."""
        pass

    @abstractmethod
    def crear_movimiento_salida(
        self,
        db: Session,
        id_insumo: int,
        id_lote: int,
        cantidad: Decimal,
        stock_anterior: Decimal,
        stock_nuevo: Decimal,
        id_user: int,
        id_documento_origen: int,
        observaciones: str
    ) -> MovimientoInsumo:
        """Crea un movimiento de salida de insumo."""
        pass

    @abstractmethod
    def descontar_insumo_fefo(
        self,
        db: Session,
        id_insumo: int,
        cantidad_requerida: Decimal,
        id_user: int,
        id_receta: int,
        nombre_receta: str
    ) -> int:
        """Descuenta la cantidad requerida de un insumo usando FEFO."""
        pass

    @abstractmethod
    def crear_produccion(
        self,
        db: Session,
        id_receta: int,
        cantidad_batch: Decimal,
        id_user: int,
        observaciones: str = None
    ) -> Dict[str, Any]:
        """Crea un registro de producción."""
        pass

    @abstractmethod
    def get_id_producto_de_receta(self, db: Session, id_receta: int) -> Optional[int]:
        """Obtiene el id_producto asociado a una receta."""
        pass

    @abstractmethod
    def incrementar_stock_producto_terminado(
        self,
        db: Session,
        id_producto: int,
        cantidad: Decimal
    ) -> Decimal:
        """Incrementa el stock de un producto terminado."""
        pass

    @abstractmethod
    def get_stock_producto_terminado(self, db: Session, id_producto: int) -> Decimal:
        """Obtiene el stock actual de un producto terminado."""
        pass

    @abstractmethod
    def crear_movimiento_producto_terminado(
        self,
        db: Session,
        id_producto: int,
        cantidad: Decimal,
        stock_anterior: Decimal,
        stock_nuevo: Decimal,
        id_user: int,
        id_produccion: int,
        observaciones: str
    ) -> int:
        """Crea un movimiento de entrada de producto terminado."""
        pass

    @abstractmethod
    def get_historial_producciones(
        self,
        db: Session,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial de producción con filtros."""
        pass

    @abstractmethod
    def get_trazabilidad_produccion(self, db: Session, id_produccion: int) -> Optional[Dict[str, Any]]:
        """Obtiene la trazabilidad completa de una producción."""
        pass
