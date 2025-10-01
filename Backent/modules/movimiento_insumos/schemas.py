from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import datetime
from enums.tipo_movimiento import TipoMovimientoEnum

class MovimientoInsumoBase(BaseModel):
    numero_movimiento: str
    id_insumo: int
    tipo_movimiento: TipoMovimientoEnum
    motivo: str
    cantidad: Decimal
    stock_anterior: Decimal
    stock_nuevo: Decimal
    id_user: int
    id_documento_origen: Optional[int] = None
    tipo_documento_origen: Optional[str] = None
    observaciones: Optional[str] = None

class MovimientoInsumoCreate(MovimientoInsumoBase):
    pass

class MovimientoInsumo(MovimientoInsumoBase):
    id_movimiento: int
    fecha_movimiento: datetime.datetime
    anulado: bool

    class Config:
        from_attributes = True
