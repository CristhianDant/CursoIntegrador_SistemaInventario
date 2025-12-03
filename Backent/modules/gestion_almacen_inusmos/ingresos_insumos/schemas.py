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

class IngresoProductoDetalleUpdate(IngresoProductoDetalleBase):
    """Schema para actualizar detalles - incluye id_ingreso_detalle opcional para identificar detalles existentes"""
    id_ingreso_detalle: Optional[int] = None  # Si se proporciona, se actualiza; si no, se crea nuevo

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
    fecha_registro: datetime.datetime = datetime.datetime.now()
    fecha_ingreso: datetime.datetime
    fecha_documento: datetime.datetime
    id_user: int
    id_proveedor: int
    observaciones: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.COMPLETADO
    monto_total: Optional[Decimal] = 0
    anulado: bool = False

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
    detalles: Optional[List[IngresoProductoDetalleUpdate]] = None  # Usa Update para poder enviar id_ingreso_detalle

class IngresoProducto(IngresoProductoBase):
    id_ingreso: int
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


# Schemas para FEFO con total y datos de proveedor
class LoteConProveedorResponse(BaseModel):
    """Schema para respuesta de lote con información del proveedor e ingreso"""
    id_ingreso_detalle: int
    id_ingreso: int
    cantidad_ingresada: Decimal
    cantidad_restante: Decimal
    precio_unitario: Decimal
    subtotal: Decimal
    fecha_vencimiento: Optional[datetime.datetime] = None
    # Datos del ingreso padre
    numero_ingreso: str
    fecha_ingreso: datetime.datetime
    # Datos del proveedor
    nombre_proveedor: str

    class Config:
        from_attributes = True


class InsumoLotesConTotalResponse(BaseModel):
    """Schema para respuesta con información del insumo, total de stock y lotes FEFO con proveedor"""
    id_insumo: int
    codigo_insumo: str
    nombre_insumo: str
    unidad_medida: str
    total_cantidad_restante: Decimal
    cantidad_lotes: int
    lotes: List[LoteConProveedorResponse] = []

    class Config:
        from_attributes = True
