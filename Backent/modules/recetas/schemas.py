from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
import datetime
from enums.estado import EstadoEnum

# Detalle de la receta
class RecetaDetalleBase(BaseModel):
    id_insumo: int
    cantidad: Decimal
    costo_unitario: Optional[Decimal] = 0
    costo_total: Optional[Decimal] = 0
    es_opcional: Optional[bool] = False
    observaciones: Optional[str] = None

class RecetaDetalleCreate(RecetaDetalleBase):
    pass

class RecetaDetalleUpdate(RecetaDetalleBase):
    pass

class RecetaDetalle(RecetaDetalleBase):
    id_receta_detalle: int
    id_receta: int

    class Config:
        from_attributes = True

# Receta
class RecetaBase(BaseModel):
    id_producto: int
    codigo_receta: str
    nombre_receta: str
    descripcion: Optional[str] = None
    rendimiento_producto_terminado: Decimal
    costo_estimado: Optional[Decimal] = 0
    version: Optional[Decimal] = 1.0
    estado: EstadoEnum = EstadoEnum.ACTIVA

class RecetaCreate(RecetaBase):
    detalles: List[RecetaDetalleCreate]

class RecetaUpdate(RecetaBase):
    detalles: Optional[List[RecetaDetalleUpdate]] = None

class Receta(RecetaBase):
    id_receta: int
    fecha_creacion: datetime.datetime
    anulado: bool
    detalles: List[RecetaDetalle] = []

    class Config:
        from_attributes = True

# Schema optimizado para Frontend (sin detalles para evitar exceso de datos)
class RecetaSimple(BaseModel):
    """Schema simplificado para listados y selecciones en Frontend"""
    id_receta: int
    nombre_receta: str
    costo_estimado: Decimal
    
    class Config:
        from_attributes = True
