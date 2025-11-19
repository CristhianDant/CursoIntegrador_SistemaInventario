from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "codigo_producto": "PROD001",
                "nombre": "Pan Integral",
                "descripcion": "Pan integral de trigo 500g",
                "unidad_medida": "KG",
                "stock_minimo": 10,
                "vida_util_dias": 3,
                "precio_venta": 2.50
            }
        }
    )

class ProductoTerminadoUpdate(ProductoTerminadoBase):
    anulado: Optional[bool] = False

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "codigo_producto": "PROD001",
                "nombre": "Pan Integral Premium",
                "descripcion": "Pan integral de trigo premium 500g",
                "unidad_medida": "KG",
                "stock_minimo": 15,
                "vida_util_dias": 5,
                "precio_venta": 3.50,
                "anulado": False
            }
        }
    )

class ProductoTerminado(ProductoTerminadoBase):
    id_producto: int
    stock_actual: Decimal
    fecha_registro: datetime.datetime
    anulado: bool

    class Config:
        from_attributes = True
