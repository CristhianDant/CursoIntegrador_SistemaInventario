from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
import datetime
from enums.unidad_medida import UnidadMedidaEnum

class ProductoTerminadoBase(BaseModel):
    codigo_producto: str
    nombre: str
    descripcion: Optional[str] = None
    unidad_medida: UnidadMedidaEnum
    stock_minimo: Optional[Decimal] = 0
    vida_util_dias: Optional[int] = None
    precio_venta: Optional[Decimal] = 0

class ProductoTerminadoCreate(ProductoTerminadoBase):
    pass

class ProductoTerminadoUpdate(ProductoTerminadoBase):
    anulado: Optional[bool] = False

class ProductoTerminado(ProductoTerminadoBase):
    id_producto: int
    stock_actual: Decimal
    fecha_registro: datetime.datetime
    anulado: bool

    class Config:
        orm_mode = True
