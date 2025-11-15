from pydantic import BaseModel, EmailStr
from typing import List

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    nombre: str | None = None
    es_admin: bool | None = None
    permisos: List[dict] = []

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserPermission(BaseModel):
    modulo: str
    accion: str

class LoginResponse(BaseModel):
    token: Token
    permisos: List[UserPermission]

