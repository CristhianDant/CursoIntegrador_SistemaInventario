from pydantic import BaseModel, EmailStr
from typing import List, Set

from modules.Gestion_Usuarios.roles.schemas import RolResponse


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
    nombre: str | None = None
    roles: List[str] = []
    permisos: Set[str] = set()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: Token
    roles: List[RolResponse]
    nombre: str
    email: EmailStr
