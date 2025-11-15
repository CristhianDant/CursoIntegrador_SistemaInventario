from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Esquemas para Rol ---
class RolBase(BaseModel):
    nombre_rol: str
    descripcion_rol: Optional[str] = None

class RolCreate(RolBase):
    pass

class RolUpdate(RolBase):
    anulado: Optional[bool] = None

class Rol(RolBase):
    id_rol: int
    anulado: bool

    class Config:
        orm_mode = True

# --- Esquemas para UsuarioRol ---
class UsuarioRolBase(BaseModel):
    id_user: int
    id_rol: int

class UsuarioRolCreate(UsuarioRolBase):
    pass

class UsuarioRol(UsuarioRolBase):
    id_user_rol: int
    fecha_asignacion: datetime
    anulado: bool

    class Config:
        orm_mode = True

# --- Esquemas para RolPermiso ---
class RolPermisoBase(BaseModel):
    id_rol: int
    id_permiso: int

class RolPermisoCreate(RolPermisoBase):
    pass

class RolPermiso(RolPermisoBase):
    id_rol_permiso: int
    fecha_asignacion: datetime
    anulado: bool

    class Config:
        orm_mode = True

