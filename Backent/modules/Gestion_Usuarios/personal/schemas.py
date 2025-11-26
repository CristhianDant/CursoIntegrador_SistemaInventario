from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
import datetime
from enums.area_personal import AreaPersonal


class PersonalBase(BaseModel):
    nombre_completo: str = Field(..., max_length=255)
    direccion: Optional[str] = None
    referencia: Optional[str] = None
    dni: str = Field(..., max_length=20)
    area: Optional[AreaPersonal] = None
    salario: Decimal = Field(default=Decimal('0'), ge=0)


class PersonalCreate(PersonalBase):
    """Schema para crear Personal (usado dentro de UsuarioCreate)"""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre_completo": "Juan Carlos Pérez García",
                    "direccion": "Av. Principal 123, Lima",
                    "referencia": "Frente al parque central",
                    "dni": "12345678",
                    "area": "PRODUCCION",
                    "salario": 2500.00
                }
            ]
        }
    }


class PersonalUpdate(BaseModel):
    """Schema para actualizar Personal"""
    nombre_completo: Optional[str] = Field(None, max_length=255)
    direccion: Optional[str] = None
    referencia: Optional[str] = None
    dni: Optional[str] = Field(None, max_length=20)
    area: Optional[AreaPersonal] = None
    salario: Optional[Decimal] = Field(None, ge=0)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre_completo": "Juan Carlos Pérez García",
                    "direccion": "Nueva dirección 456",
                    "area": "ADMINISTRACION",
                    "salario": 3000.00
                }
            ]
        }
    }


class PersonalResponse(PersonalBase):
    """Schema de respuesta para Personal"""
    id_personal: int
    id_usuario: int
    anulado: bool
    fecha_registro: datetime.datetime

    model_config = {"from_attributes": True}
