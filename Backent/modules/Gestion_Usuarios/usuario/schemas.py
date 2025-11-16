from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import datetime

class UsuarioBase(BaseModel):
    nombre: str
    apellidos: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., max_length=70)

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, max_length=70)
    anulado: Optional[bool] = None

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
