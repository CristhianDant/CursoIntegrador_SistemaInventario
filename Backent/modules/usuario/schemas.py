from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class UsuarioBase(BaseModel):
    nombre: str
    apellidos: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    anulado: Optional[bool] = None

class Usuario(UsuarioBase):
    id_user: int
    es_admin: bool
    fecha_registro: datetime.datetime
    ultimo_acceso: Optional[datetime.datetime] = None
    anulado: bool

    class Config:
        orm_mode = True

