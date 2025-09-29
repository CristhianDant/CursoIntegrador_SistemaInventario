from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class EmpresaBase(BaseModel):
    nombre_empresa: str
    ruc: str
    direccion: str
    telefono: str
    email: EmailStr

class EmpresaCreate(EmpresaBase):
    pass

class EmpresaUpdate(BaseModel):
    nombre_empresa: Optional[str] = None
    ruc: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    estado: Optional[bool] = None

class Empresa(EmpresaBase):
    id_empresa: int
    estado: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True
