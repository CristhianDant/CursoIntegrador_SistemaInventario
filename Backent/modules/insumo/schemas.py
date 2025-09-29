from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InsumoBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=255)
    descripcion: Optional[str] = None
    unidad_medida: str = Field(..., max_length=50)
    stock_actual: float
    stock_minimo: float
    fecha_caducidad: Optional[datetime] = None
    perecible: bool = False
    precio_promedio: Optional[float] = None
    categoria: Optional[str] = Field(None, max_length=100)

class InsumoCreate(InsumoBase):
    pass

class InsumoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=50)
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    unidad_medida: Optional[str] = Field(None, max_length=50)
    stock_actual: Optional[float] = None
    stock_minimo: Optional[float] = None
    fecha_caducidad: Optional[datetime] = None
    perecible: Optional[bool] = None
    precio_promedio: Optional[float] = None
    categoria: Optional[str] = Field(None, max_length=100)
    anulado: Optional[bool] = None

class Insumo(InsumoBase):
    id_insumo: int
    fecha_registro: datetime
    anulado: bool

    class Config:
        orm_mode = True

