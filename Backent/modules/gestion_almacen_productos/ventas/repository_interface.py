from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import date


class VentasRepositoryInterface(ABC):
    """Interfaz para el repositorio de ventas."""
    
    @abstractmethod
    def generar_numero_venta(self, db: Session) -> str:
        """Genera un número único de venta."""
        pass
    
    @abstractmethod
    def crear_venta(
        self, 
        db: Session, 
        numero_venta: str,
        total: Decimal,
        metodo_pago: str,
        id_user: int,
        observaciones: Optional[str]
    ) -> Dict[str, Any]:
        """Crea un registro de venta y retorna el id_venta."""
        pass
    
    @abstractmethod
    def crear_detalle_venta(
        self,
        db: Session,
        id_venta: int,
        id_producto: int,
        cantidad: Decimal,
        precio_unitario: Decimal,
        descuento_porcentaje: Decimal,
        subtotal: Decimal
    ) -> int:
        """Crea un detalle de venta y retorna el id_detalle."""
        pass
    
    @abstractmethod
    def get_stock_producto(self, db: Session, id_producto: int) -> Decimal:
        """Obtiene el stock actual de un producto terminado."""
        pass
    
    @abstractmethod
    def descontar_stock_producto(
        self, 
        db: Session, 
        id_producto: int, 
        cantidad: Decimal
    ) -> Decimal:
        """Descuenta stock de un producto y retorna el nuevo stock."""
        pass
    
    @abstractmethod
    def get_producto_info(self, db: Session, id_producto: int) -> Optional[Dict[str, Any]]:
        """Obtiene información de un producto terminado."""
        pass
    
    @abstractmethod
    def get_venta_por_id(self, db: Session, id_venta: int) -> Optional[Dict[str, Any]]:
        """Obtiene una venta por ID con sus detalles."""
        pass
    
    @abstractmethod
    def get_ventas_del_dia(self, db: Session, fecha: date) -> List[Dict[str, Any]]:
        """Obtiene todas las ventas de un día específico."""
        pass
    
    @abstractmethod
    def get_productos_disponibles(self, db: Session) -> List[Dict[str, Any]]:
        """Obtiene productos con stock disponible para venta."""
        pass
    
    @abstractmethod
    def anular_venta(self, db: Session, id_venta: int) -> bool:
        """Marca una venta como anulada."""
        pass
    
    @abstractmethod
    def get_ultima_produccion_producto(
        self, 
        db: Session, 
        id_producto: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene la fecha de la última producción de un producto."""
        pass
