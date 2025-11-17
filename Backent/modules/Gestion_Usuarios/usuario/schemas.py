from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
import datetime
from modules.Gestion_Usuarios.roles.schemas import RolResponse

class UsuarioBase(BaseModel):
    nombre: str
    apellidos: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., max_length=70)
    lista_roles: List[int] = []
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre": "Juan",
                    "apellidos": "Perez",
                    "email": "juan.perez@example.com",
                    "password": "una_contraseña_segura",
                    "lista_roles": [1, 2]
                }
            ]
        }
    }

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, max_length=70)
    anulado: Optional[bool] = None
    lista_roles: Optional[List[int]] = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre": "Juan Alberto",
                    "apellidos": "Perez Garcia",
                    "email": "juan.perez.garcia@example.com",
                    "password": "una_nueva_contraseña",
                    "anulado": False,
                    "lista_roles": [1, 3]
                }
            ]
        }
    }

class Usuario(UsuarioBase):
    id_user: int
    fecha_registro: datetime.datetime
    ultimo_acceso: Optional[datetime.datetime] = None
    anulado: bool

    model_config = {"from_attributes": True}


class UsuarioResponse(UsuarioBase):
    id_user: int
    fecha_registro: datetime.datetime
    ultimo_acceso: Optional[datetime.datetime] = None
    anulado: bool

    model_config = {"from_attributes": True}


class UsuarioResponseRol(UsuarioResponse):
    lista_roles: List[RolResponse] = Field(..., alias='roles')

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id_user": 1,
                    "nombre": "Juan",
                    "apellidos": "Perez",
                    "email": "juan.perez@example.com",
                    "fecha_registro": "2023-01-01T12:00:00",
                    "ultimo_acceso": "2023-01-10T15:30:00",
                    "anulado": False,
                    "lista_roles": [
                        {
                            "id_rol": 1,
                            "nombre_rol": "Administrador",
                            "descripcion": "Acceso total al sistema",
                            "anulado": False
                        },
                        {
                            "id_rol": 2,
                            "nombre_rol": "Vendedor",
                            "descripcion": "Acceso al módulo de ventas",
                            "anulado": False
                        }
                    ]
                }
            ]
        }
    }
