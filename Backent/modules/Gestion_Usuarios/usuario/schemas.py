from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
import datetime
from modules.Gestion_Usuarios.roles.schemas import RolResponse
from modules.Gestion_Usuarios.personal.schemas import PersonalCreate, PersonalUpdate, PersonalResponse

class UsuarioBase(BaseModel):
    nombre: str
    apellidos: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., max_length=70)
    lista_roles: List[int] = []
    personal: PersonalCreate  # Datos de personal requeridos
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre": "Maria",
                    "apellidos": "Garcia",
                    "email": "maria.garcia@example.com",
                    "password": "contraseña_segura_123",
                    "lista_roles": [1],
                    "personal": {
                        "nombre_completo": "Maria Elena Garcia Lopez",
                        "direccion": "Calle Los Pinos 456",
                        "referencia": "Cerca al mercado central",
                        "dni": "87654321",
                        "area": "ADMINISTRACION",
                        "salario": 3000.00
                    }
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
    personal: Optional[PersonalUpdate] = None  # Datos de personal opcionales
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nombre": "Juan Alberto",
                    "apellidos": "Perez Garcia",
                    "email": "juan.perez.garcia@example.com",
                    "password": "una_nueva_contraseña",
                    "anulado": False,
                    "lista_roles": [1, 3],
                    "personal": {
                        "nombre_completo": "Juan Alberto Pérez García",
                        "direccion": "Nueva dirección 456",
                        "area": "ADMINISTRACION",
                        "salario": 3000.00
                    }
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


class UsuarioResponseConPersonal(UsuarioResponse):
    """Respuesta de Usuario con datos de Personal incluidos"""
    lista_roles: List[RolResponse] = Field(default=[], alias='roles')
    personal: Optional[PersonalResponse] = None

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
                        }
                    ],
                    "personal": {
                        "id_personal": 1,
                        "id_usuario": 1,
                        "nombre_completo": "Juan Carlos Pérez García",
                        "direccion": "Av. Principal 123, Lima",
                        "referencia": "Frente al parque central",
                        "dni": "12345678",
                        "area": "PRODUCCION",
                        "salario": 2500.00,
                        "anulado": False,
                        "fecha_registro": "2023-01-01T12:00:00"
                    }
                }
            ]
        }
    }
