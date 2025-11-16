from pydantic import BaseModel
from typing import Optional

class RolBase(BaseModel):
    nombre_rol: str

class RolCreate(RolBase):
    pass

class RolUpdate(BaseModel):
    nombre_rol: Optional[str] = None
    anulado: Optional[bool] = None

class Rol(RolBase):
    id_rol: int
    anulado: bool

    class Config:
        from_attributes = True

class RolResponse(RolBase):
    id_rol: int
    anulado: bool

    class Config:
        from_attributes = True

