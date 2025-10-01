    tipo_movimiento: TipoMovimientoEnum
    motivo: str
    cantidad: Decimal
    precio_venta: Optional[Decimal] = 0
    id_user: int
    id_documento_origen: Optional[int] = None
    tipo_documento_origen: Optional[str] = None
    observaciones: Optional[str] = None

class MovimientoProductoTerminadoCreate(MovimientoProductoTerminadoBase):
    pass

class MovimientoProductoTerminado(MovimientoProductoTerminadoBase):
    id_movimiento: int
    fecha_movimiento: datetime.datetime
    anulado: bool

    class Config:
        from_attributes = True
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import datetime
from enums.tipo_movimiento import TipoMovimientoEnum

class MovimientoProductoTerminadoBase(BaseModel):
    numero_movimiento: str
    id_producto: int

