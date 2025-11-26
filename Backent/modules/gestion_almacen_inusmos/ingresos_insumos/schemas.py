from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
import datetime
from enums.estado import EstadoEnum
from enums.tipo_documento import TipoDocumentoEnum

# Detalle del ingreso de producto
class IngresoProductoDetalleBase(BaseModel):
    id_insumo: int
    cantidad_ordenada: Optional[Decimal] = 0
    cantidad_ingresada: Decimal
    precio_unitario: Decimal
    subtotal: Decimal
    fecha_vencimiento: Optional[datetime.datetime] = None
    cantidad_restante: Optional[Decimal] = 0

class IngresoProductoDetalleCreate(IngresoProductoDetalleBase):
    pass

class IngresoProductoDetalle(IngresoProductoDetalleBase):
    id_ingreso_detalle: int
    id_ingreso: int

    class Config:
        from_attributes = True

# Ingreso de producto
class IngresoProductoBase(BaseModel):
    numero_ingreso: str
    id_orden_compra: Optional[int] = None
    numero_documento: str
    tipo_documento: TipoDocumentoEnum
    fecha_ingreso: datetime.datetime
    fecha_documento: datetime.datetime
    id_user: int
    id_proveedor: int
    observaciones: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.COMPLETADO
    monto_total: Optional[Decimal] = 0

class IngresoProductoCreate(IngresoProductoBase):
    detalles: List[IngresoProductoDetalleCreate]

class IngresoProductoUpdate(BaseModel):
    numero_documento: Optional[str] = None
    tipo_documento: Optional[TipoDocumentoEnum] = None
    fecha_ingreso: Optional[datetime.datetime] = None
    fecha_documento: Optional[datetime.datetime] = None
    observaciones: Optional[str] = None
    estado: Optional[EstadoEnum] = None
    monto_total: Optional[Decimal] = None
    detalles: Optional[List[IngresoProductoDetalleCreate]] = None

class IngresoProducto(IngresoProductoBase):
    id_ingreso: int
    fecha_registro: datetime.datetime
    anulado: bool
    detalles: List[IngresoProductoDetalle] = []

    class Config:
        from_attributes = True

# Schemas para FEFO
class IngresoDetalleFefoResponse(BaseModel):
    """Schema para respuesta de lotes FEFO"""
    id_ingreso_detalle: int
    id_ingreso: int
    cantidad_ingresada: Decimal
    cantidad_restante: Decimal
    precio_unitario: Decimal
    subtotal: Decimal
    fecha_vencimiento: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

class InsumoLotesFefoResponse(BaseModel):
    """Schema para respuesta con información del insumo y sus lotes FEFO"""
    id_insumo: int
    nombre_insumo: str
    lotes: List[IngresoDetalleFefoResponse] = []

    class Config:
        from_attributes = True

