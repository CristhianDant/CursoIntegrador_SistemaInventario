from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import datetime
from enums.tipo_merma import TipoMermaEnum
from enums.estado import EstadoEnum

class MermaBase(BaseModel):
    numero_registro: str
    tipo: TipoMermaEnum
    causa: str
    cantidad: Decimal
    costo_unitario: Optional[Decimal] = 0
    costo_total: Optional[Decimal] = 0
    fecha_caso: datetime.datetime = datetime.datetime.now()
    id_insumo: Optional[int] = None
    id_producto: Optional[int] = None
    id_user_responsable: int
    observacion: Optional[str] = None
    estado: EstadoEnum = EstadoEnum.REGISTRADO

class MermaCreate(MermaBase):
    pass

class MermaUpdate(BaseModel):
    tipo: Optional[TipoMermaEnum] = None
    causa: Optional[str] = None
    cantidad: Optional[Decimal] = None
    costo_unitario: Optional[Decimal] = None
    costo_total: Optional[Decimal] = None
    fecha_caso: Optional[datetime.datetime] = None
    id_insumo: Optional[int] = None
    id_producto: Optional[int] = None
    id_user_responsable: Optional[int] = None
    observacion: Optional[str] = None
    estado: Optional[EstadoEnum] = None

class Merma(MermaBase):
    id_merma: int
    anulado: bool

    class Config:
        from_attributes = True

