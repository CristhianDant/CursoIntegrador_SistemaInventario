from pydantic import BaseModel
from typing import Optional
import datetime

# --- Permiso Schemas (Read-only) ---
class PermisoBase(BaseModel):
    descripcion_permiso: str
    modulo: str
    accion: str

class Permiso(PermisoBase):
    id_permiso: int

    class Config:
        from_attributes = True

# --- UsuarioPermiso Schemas (Full CRUD) ---
class UsuarioPermisoBase(BaseModel):
    id_user: int
    id_permiso: int

class UsuarioPermisoCreate(UsuarioPermisoBase):
    pass

class UsuarioPermisoUpdate(BaseModel):
    anulado: bool

class UsuarioPermiso(UsuarioPermisoBase):
    id_user_permiso: int
    fecha_asignacion: datetime.datetime
    anulado: bool

    class Config:
        from_attributes = True

