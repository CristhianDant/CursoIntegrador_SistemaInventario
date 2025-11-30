from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from datetime import date
from modules.gestion_almacen_productos.ventas.schemas import (
    RegistrarVentaRequest,
    VentaResponse,
    VentaResumenResponse,
    ProductoDisponibleResponse,
    VentasDelDiaResponse
)


class VentasServiceInterface(ABC):
    """Interfaz para el servicio de ventas."""
    
    @abstractmethod
    def registrar_venta(
        self,
        db: Session,
        request: RegistrarVentaRequest,
        id_user: int
    ) -> VentaResponse:
        """
        Registra una venta completa:
        1. Valida stock disponible
        2. Crea venta y detalles
        3. Descuenta stock de productos
        4. Crea movimientos de salida
        """
        pass
    
    @abstractmethod
    def get_venta_por_id(self, db: Session, id_venta: int) -> VentaResponse:
        """Obtiene una venta por ID con todos sus detalles."""
        pass
    
    @abstractmethod
    def get_ventas_del_dia(self, db: Session, fecha: date) -> VentasDelDiaResponse:
        """Obtiene todas las ventas de un día específico."""
        pass
    
    @abstractmethod
    def get_productos_disponibles(self, db: Session) -> List[ProductoDisponibleResponse]:
        """Obtiene productos disponibles para venta con descuentos sugeridos."""
        pass
    
    @abstractmethod
    def anular_venta(self, db: Session, id_venta: int, id_user: int) -> VentaResponse:
        """
        Anula una venta y restaura el stock:
        1. Marca venta como anulada
        2. Restaura stock de productos
        3. Crea movimientos de entrada (compensación)
        """
        pass
