from pydantic import BaseModel
from typing import Optional, List
from modules.Gestion_Usuarios.permisos.schemas import PermisoResponse

class RolBase(BaseModel):
    nombre_rol: str
    descripcion: Optional[str] = None

class RolCreate(RolBase):
    lista_permisos: List[int] = []
    pass

class RolUpdate(BaseModel):
    nombre_rol: Optional[str] = None
    descripcion: Optional[str] = None
    anulado: Optional[bool] = None

class Rol(RolBase):
    id_rol: int
    anulado: bool

    model_config = {"from_attributes": True}

class RolResponse(RolBase):
    id_rol: int
    anulado: bool

    model_config = {"from_attributes": True}


class RolResponsePermisos(BaseModel):
    nombre_rol: str
    descripcion: Optional[str] = None
    lista_permisos: List[PermisoResponse] = []

    model_config = {"from_attributes": True}
