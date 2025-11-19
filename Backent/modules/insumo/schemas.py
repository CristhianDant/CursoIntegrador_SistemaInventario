from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enums.unidad_medida import UnidadMedidaEnum
from enums.categoria_insumo import CategoriaInsumoEnum

class InsumoBase(BaseModel):
    codigo: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=255)
    descripcion: Optional[str] = None
    unidad_medida: UnidadMedidaEnum
    stock_minimo: Optional[Decimal] = 0
    perecible: Optional[bool] = False
    categoria: Optional[CategoriaInsumoEnum] = None

class InsumoCreate(InsumoBase):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "codigo": "INS002",
                    "nombre": "Azúcar Blanca",
                    "descripcion": "Azúcar blanca refinada",
                    "unidad_medida": "KG",
                    "stock_minimo": 5,
                    "perecible": False,
                    "categoria": "Edulcorantes"
                }
            ]
        }
    }

class InsumoUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    unidad_medida: Optional[UnidadMedidaEnum] = None
    stock_minimo: Optional[Decimal] = None
    perecible: Optional[bool] = None
    categoria: Optional[CategoriaInsumoEnum] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre": "Harina de Trigo Premium",
                    "descripcion": "Harina de trigo premium para repostería de alta calidad",
                    "stock_minimo": 15
                },
                {
                    "codigo": "INS002",
                    "perecible": True,
                    "categoria": "Chocolates"
                }
            ]
        }
    }

class Insumo(InsumoBase):
    id_insumo: int
    fecha_registro: datetime
    anulado: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id_insumo": 1,
                    "codigo": "INS001",
                    "nombre": "Harina de Trigo",
                    "descripcion": "Harina de trigo premium para repostería",
                    "unidad_medida": "KG",
                    "stock_minimo": 10,
                    "perecible": True,
                    "categoria": "Harinas",
                    "fecha_registro": "2025-01-15T10:30:00",
                    "anulado": False
                },
                {
                    "id_insumo": 2,
                    "codigo": "INS002",
                    "nombre": "Azúcar Blanca",
                    "descripcion": "Azúcar blanca refinada",
                    "unidad_medida": "KG",
                    "stock_minimo": 5,
                    "perecible": False,
                    "categoria": "Edulcorantes",
                    "fecha_registro": "2025-01-16T14:20:00",
                    "anulado": False
                }
            ]
        }
    }

