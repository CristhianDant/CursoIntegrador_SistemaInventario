from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class EmailCreate(BaseModel):
    destinatario: EmailStr
    asunto: str
    cuerpo_html: str


class EmailResponse(BaseModel):
    id_email: int
    destinatario: str
    asunto: str
    estado: str
    intentos: int
    ultimo_error: Optional[str] = None
    fecha_creacion: datetime
    fecha_envio: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ColaEmailStats(BaseModel):
    pendientes: int
    enviados: int
    errores: int
    total: int


class CredencialesEmailData(BaseModel):
    """Datos necesarios para enviar email de credenciales"""
    nombre_completo: str
    email: EmailStr
    password: str  # Password en texto plano (antes del hash)
