from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enums.unidad_medida import UnidadMedidaEnum

class InsumoBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=255)
    descripcion: Optional[str] = None
    unidad_medida: UnidadMedidaEnum
    stock_minimo: Optional[Decimal] = 0
    perecible: Optional[bool] = False
    categoria: Optional[str] = None

class InsumoCreate(InsumoBase):
    pass

class InsumoUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    unidad_medida: Optional[UnidadMedidaEnum] = None
    stock_minimo: Optional[Decimal] = None
    perecible: Optional[bool] = None
    categoria: Optional[str] = None

class Insumo(InsumoBase):
    id_insumo: int
    stock_actual: Decimal
    precio_promedio: Optional[Decimal] = 0
    fecha_registro: datetime
    anulado: bool

    class Config:
        from_attributes = True
