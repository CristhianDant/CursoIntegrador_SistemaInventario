from pydantic import BaseModel
from typing import Optional, List
from modules.Gestion_Usuarios.permisos.schemas import PermisoResponse

class RolBase(BaseModel):
    nombre_rol: str
    descripcion: Optional[str] = None

class RolCreate(RolBase):
    lista_permisos: List[int] = []
    model_config = {
        "json_schema_extra": {
            "example": {
                "nombre_rol": "Nuevo Rol",
                "descripcion": "Descripción del nuevo rol",
                "lista_permisos": [1, 2]
            }
        }
    }

class RolUpdate(BaseModel):
    id_rol: int
    nombre_rol: Optional[str] = None
    descripcion: Optional[str] = None
    anulado: Optional[bool] = None
    lista_permisos: Optional[List[int]] = None
    model_config = {
        "json_schema_extra": {
            "example": {
                "id_rol": 1,
                "nombre_rol": "Rol Actualizado",
                "descripcion": "Descripción actualizada",
                "anulado": False,
                "lista_permisos": [1, 3, 5]
            }
        }
    }

class Rol(RolBase):
    id_rol: int
    anulado: bool

    model_config = {"from_attributes": True}

class RolResponse(RolBase):
    id_rol: int
    anulado: bool

    model_config = {"from_attributes": True}


class RolResponsePermisos(BaseModel):
    id_rol: int
    anulado: bool
    nombre_rol: str
    descripcion: Optional[str] = None
    lista_permisos: List[PermisoResponse] = []

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id_rol": 1,
                "anulado": False,
                "nombre_rol": "Administrador",
                "descripcion": "Rol con todos los permisos",
                "lista_permisos": [
                    {
                        "id_permiso": 1,
                        "modulo": "USUARIOS",
                        "accion": "CREAR"
                    },
                    {
                        "id_permiso": 2,
                        "modulo": "USUARIOS",
                        "accion": "LEER"
                    }
                ]
            }
        }
    }
