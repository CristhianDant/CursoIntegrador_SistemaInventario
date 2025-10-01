from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
import datetime
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
    fecha_entrega_esperada: datetime.datetime
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
    fecha_aprobacion: Optional[datetime.datetime] = None

class OrdenDeCompraCreate(OrdenDeCompraBase):
    detalles: List[OrdenDeCompraDetalleCreate]

class OrdenDeCompraUpdate(OrdenDeCompraBase):
    detalles: Optional[List[OrdenDeCompraDetalleUpdate]] = None

class OrdenDeCompra(OrdenDeCompraBase):
    id_orden: int
    fecha_orden: datetime.datetime
    anulado: bool
    detalles: List[OrdenDeCompraDetalle] = []

    class Config:
        from_attributes = True
