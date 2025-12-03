from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, date
from enums.monedas import MonedaEnum
from enums.estado import EstadoEnum

# Detalle de la orden de compra
class OrdenDeCompraDetalleBase(BaseModel):
    id_insumo: int
    cantidad: Decimal
    precio_unitario: Decimal
    descuento_unitario: Optional[Decimal] = 0
    sub_total: Decimal
    observaciones: Optional[str] = None

class OrdenDeCompraDetalleCreate(OrdenDeCompraDetalleBase):
    pass

class OrdenDeCompraDetalleUpdate(OrdenDeCompraDetalleBase):
    pass

class OrdenDeCompraDetalle(OrdenDeCompraDetalleBase):
    id_orden_detalle: int
    id_orden: int

    class Config:
        from_attributes = True

# Orden de compra
class OrdenDeCompraBase(BaseModel):
    numero_orden: str
    id_proveedor: int
    fecha_entrega_esperada: datetime
    moneda: MonedaEnum = MonedaEnum.PEN
    tipo_cambio: Optional[Decimal] = 1
    sub_total: Decimal
    descuento: Optional[Decimal] = 0
    igv: Decimal = 0
    total: Decimal
    estado: EstadoEnum = EstadoEnum.PENDIENTE
    observaciones: Optional[str] = None
    id_user_creador: int
    id_user_aprobador: Optional[int] = None
    fecha_aprobacion: Optional[datetime] = None

class OrdenDeCompraCreate(OrdenDeCompraBase):
    detalles: List[OrdenDeCompraDetalleCreate]

class OrdenDeCompraUpdate(OrdenDeCompraBase):
    detalles: Optional[List[OrdenDeCompraDetalleUpdate]] = None

class OrdenDeCompra(OrdenDeCompraBase):
    id_orden: int
    fecha_orden: datetime
    anulado: bool
    detalles: List[OrdenDeCompraDetalle] = []

    class Config:
        from_attributes = True


# ==================== SUGERENCIAS DE COMPRA (FC-10) ====================

class ItemSugerenciaCompra(BaseModel):
    """Item individual en la sugerencia de compra."""
    id_insumo: int
    codigo: str
    nombre: str
    unidad_medida: str
    categoria: Optional[str] = None
    
    # Stock
    stock_actual: Decimal = Field(description="Stock actual disponible")
    stock_minimo: Decimal = Field(description="Stock mínimo configurado")
    deficit: Decimal = Field(description="Diferencia entre mínimo y actual")
    
    # Consumo
    consumo_diario_promedio: Decimal = Field(description="Consumo promedio diario")
    dias_stock_restante: Decimal = Field(description="Días de stock al ritmo actual")
    
    # Vencimientos
    cantidad_por_vencer: Decimal = Field(default=Decimal("0"), description="Cantidad que vence en 7 días")
    
    # Sugerencia
    cantidad_sugerida: Decimal = Field(description="Cantidad recomendada a comprar")
    urgencia: str = Field(description="inmediata (rojo) o normal (verde)")
    razon: str = Field(description="Razón de la sugerencia")
    
    # Precio
    ultimo_precio: Optional[Decimal] = Field(default=None, description="Último precio de compra")
    subtotal_estimado: Optional[Decimal] = Field(default=None, description="Cantidad × último precio")


class ProveedorSugerencia(BaseModel):
    """Agrupación de sugerencias por proveedor."""
    id_proveedor: int
    nombre_proveedor: str
    email: str
    telefono: str
    total_items: int
    total_estimado: Decimal
    items: List[ItemSugerenciaCompra]


class SugerenciaCompraResponse(BaseModel):
    """Respuesta completa de sugerencias de compra."""
    fecha_generacion: datetime
    dias_proyeccion: int = Field(description="Días de consumo proyectados")
    
    # Resumen general
    total_items: int
    total_items_urgentes: int = Field(description="Items con urgencia inmediata")
    total_estimado: Decimal
    
    # Agrupado por proveedor
    por_proveedor: List[ProveedorSugerencia]
    
    # Lista plana (sin agrupar)
    todos_items: List[ItemSugerenciaCompra]


class GenerarOrdenDesdesugerenciaRequest(BaseModel):
    """Request para generar orden desde sugerencia."""
    id_proveedor: int
    items: List[dict] = Field(description="Lista de {id_insumo, cantidad, precio_unitario}")
    fecha_entrega_esperada: datetime
    observaciones: Optional[str] = None
    id_user_creador: int


class EnviarEmailProveedorRequest(BaseModel):
    """Request para enviar email a proveedor."""
    id_proveedor: int
    items: List[dict] = Field(description="Lista de {id_insumo, cantidad, unidad_medida, ultimo_precio}")
    mensaje_adicional: Optional[str] = None


class EnviarEmailProveedorResponse(BaseModel):
    """Respuesta del envío de email."""
    enviado: bool
    mensaje: str
    email_destino: str
    fecha_envio: Optional[datetime] = None
