from pydantic import BaseModel, Field, validator
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class VentaItemRequest(BaseModel):
    """Item de venta (producto a vender)."""
    id_producto: int = Field(..., gt=0, description="ID del producto terminado")
    cantidad: Decimal = Field(..., gt=0, description="Cantidad a vender")
    precio_unitario: Decimal = Field(..., gt=0, description="Precio unitario de venta")
    descuento_porcentaje: Decimal = Field(default=Decimal("0"), ge=0, le=100, description="Descuento en porcentaje (0-100)")
    
    @validator('cantidad', 'precio_unitario', 'descuento_porcentaje')
    def validar_decimales(cls, v):
        """Validar que los decimales sean positivos."""
        if v < 0:
            raise ValueError("El valor debe ser positivo")
        return v


class RegistrarVentaRequest(BaseModel):
    """Request para registrar una venta."""
    items: List[VentaItemRequest] = Field(..., min_items=1, description="Lista de productos a vender")
    metodo_pago: str = Field(..., description="Método de pago: efectivo, tarjeta, transferencia")
    observaciones: Optional[str] = Field(default=None, max_length=500, description="Observaciones de la venta")
    
    @validator('metodo_pago')
    def validar_metodo_pago(cls, v):
        """Validar que el método de pago sea válido."""
        metodos_validos = ['efectivo', 'tarjeta', 'transferencia']
        if v.lower() not in metodos_validos:
            raise ValueError(f"Método de pago inválido. Debe ser uno de: {', '.join(metodos_validos)}")
        return v.lower()


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class VentaDetalleResponse(BaseModel):
    """Detalle de un item de venta."""
    id_detalle: int
    id_producto: int
    nombre_producto: str
    cantidad: Decimal
    precio_unitario: Decimal
    descuento_porcentaje: Decimal
    subtotal: Decimal
    
    class Config:
        from_attributes = True


class VentaResponse(BaseModel):
    """Response de una venta completa."""
    id_venta: int
    numero_venta: str
    fecha_venta: datetime
    total: Decimal
    metodo_pago: str
    id_user: int
    nombre_usuario: str
    observaciones: Optional[str]
    anulado: bool
    detalles: List[VentaDetalleResponse]
    
    class Config:
        from_attributes = True


class VentaResumenResponse(BaseModel):
    """Resumen de venta (sin detalles)."""
    id_venta: int
    numero_venta: str
    fecha_venta: datetime
    total: Decimal
    metodo_pago: str
    nombre_usuario: str
    cantidad_items: int
    anulado: bool
    
    class Config:
        from_attributes = True


class ProductoDisponibleResponse(BaseModel):
    """Producto disponible para venta."""
    id_producto: int
    codigo_producto: str
    nombre: str
    descripcion: Optional[str]
    stock_actual: Decimal
    precio_venta: Decimal
    dias_desde_produccion: Optional[int]
    descuento_sugerido: Decimal
    
    class Config:
        from_attributes = True


class VentasDelDiaResponse(BaseModel):
    """Resumen de ventas del día."""
    fecha: datetime
    total_ventas: int
    monto_total: Decimal
    ventas: List[VentaResumenResponse]
    
    class Config:
        from_attributes = True
