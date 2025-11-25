from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import datetime
from enums.tipo_movimiento import TipoMovimientoEnum

class MovimientoInsumoBase(BaseModel):
    numero_movimiento: str
    id_insumo: int
    id_lote: Optional[int] = None
    tipo_movimiento: TipoMovimientoEnum
    motivo: str
    cantidad: Decimal
    stock_anterior_lote: Optional[Decimal] = None
    stock_nuevo_lote: Optional[Decimal] = None
    fecha_movimiento: datetime.datetime = datetime.datetime.now()
    id_user: int
    id_documento_origen: Optional[int] = None
    tipo_documento_origen: Optional[str] = None
    observaciones: Optional[str] = None
    anulado: bool = False

class MovimientoInsumoCreate(MovimientoInsumoBase):
    pass

class MovimientoInsumo(MovimientoInsumoBase):
    id_movimiento: int
    id_lote: Optional[int] = None

    class Config:
        from_attributes = True
