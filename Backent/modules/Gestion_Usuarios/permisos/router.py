from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from .schemas import Permiso, UsuarioPermiso, UsuarioPermisoCreate
from .service import PermisosService
from utils.standard_responses import api_response_ok, api_response_not_found

router = APIRouter()
service = PermisosService()

# --- Endpoints para Permisos (Read-Only) ---

@router.get("/permisos", response_model=List[Permiso])
def get_all_permisos(db: Session = Depends(get_db)):
    permisos = service.get_all_permisos(db)
    return api_response_ok(permisos)

# --- Endpoints para UsuarioPermisos (CRUD) ---

@router.get("/usuario-permisos", response_model=List[UsuarioPermiso])
def get_all_usuario_permisos(db: Session = Depends(get_db)):
    usuario_permisos = service.get_all_usuario_permisos(db)
    return api_response_ok(usuario_permisos)

@router.get("/usuario-permisos/{usuario_permiso_id}", response_model=UsuarioPermiso)
def get_usuario_permiso_by_id(usuario_permiso_id: int, db: Session = Depends(get_db)):
    usuario_permiso = service.get_usuario_permiso_by_id(db, usuario_permiso_id)
    if usuario_permiso is None:
        return api_response_not_found("Permiso de usuario no encontrado")
    return api_response_ok(usuario_permiso)

@router.post("/usuario-permisos", response_model=UsuarioPermiso, status_code=201)
def create_usuario_permiso(usuario_permiso: UsuarioPermisoCreate, db: Session = Depends(get_db)):
    nuevo_permiso = service.create_usuario_permiso(db, usuario_permiso)
    return api_response_ok(nuevo_permiso)

@router.delete("/usuario-permisos/{usuario_permiso_id}")
def delete_usuario_permiso(usuario_permiso_id: int, db: Session = Depends(get_db)):
    deleted = service.delete_usuario_permiso(db, usuario_permiso_id)
    if not deleted:
        return api_response_not_found("Permiso de usuario no encontrado")
    return api_response_ok({"detail": "Permiso de usuario eliminado (anulado)"})

