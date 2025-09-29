from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ProveedorBase(BaseModel):
    nombre: str
    ruc_dni: str
    numero_contacto: str
    email_contacto: str
    direccion_fiscal: str

class ProveedorCreate(ProveedorBase):
    pass

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    ruc_dni: Optional[str] = None
    numero_contacto: Optional[str] = None
    email_contacto: Optional[str] = None
    direccion_fiscal: Optional[str] = None
    anulado: Optional[bool] = None

class Proveedor(ProveedorBase):
    id_proveedor: int
    anulado: bool
    fecha_registro: datetime

    model_config = ConfigDict(from_attributes=True)

