from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from modules.usuario.schemas import UsuarioResponse, UsuarioCreate, UsuarioUpdate
from modules.usuario.service import UsuarioService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()
service = UsuarioService()

@router.get("/", response_model=List[UsuarioResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = service.get_all(db)
    return api_response_ok(users)

@router.get("/{user_id}", response_model=UsuarioResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = service.get_by_id(db, user_id)
    if user is None:
        return api_response_not_found("Usuario no encontrado")
    return api_response_ok(user)

@router.post("/", response_model=UsuarioResponse, status_code=201)
def create_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = service.get_by_email(db, email=user.email)
    if db_user:
        return api_response_bad_request("El correo electrónico ya está registrado")
    new_user = service.create(db, user)
    return api_response_ok(new_user)

@router.put("/{user_id}", response_model=UsuarioResponse)
def update_user(user_id: int, user_update: UsuarioUpdate, db: Session = Depends(get_db)):
    user = service.update(db, user_id, user_update)
    if user is None:
        return api_response_not_found("Usuario no encontrado")
    return api_response_ok(user)

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, user_id)
    if not deleted:
        return api_response_not_found("Usuario no encontrado")
    return api_response_ok({"detail": "Usuario eliminado"})
