from pydantic import BaseModel
from typing import Optional
from enums.tipo_modulo import TipoModulo

class PermisoBase(BaseModel):
    modulo: TipoModulo
    accion: str

class PermisoCreate(PermisoBase):
    pass

class PermisoUpdate(BaseModel):
    modulo: Optional[TipoModulo] = None
    accion: Optional[str] = None

class Permiso(PermisoBase):
    id_permiso: int

    model_config = {"from_attributes": True}

class PermisoResponse(PermisoBase):
    id_permiso: int

    model_config = {"from_attributes": True}
