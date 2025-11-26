from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from .schemas import UsuarioResponse, UsuarioCreate, UsuarioUpdate, UsuarioResponseRol, UsuarioResponseConPersonal
from .service import UsuarioService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()
service = UsuarioService()

@router.get("/", response_model=List[UsuarioResponseConPersonal])
def get_all_users(db: Session = Depends(get_db)):
    users = service.get_all(db)
    return api_response_ok(users)

@router.get("/{user_id}", response_model=UsuarioResponseConPersonal)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = service.get_by_id(db, user_id)
    if user is None:
        return api_response_not_found("Usuario no encontrado")

    response_user = UsuarioResponseConPersonal.model_validate(user)
    return api_response_ok(response_user)

@router.post("/", response_model=UsuarioResponseConPersonal, status_code=201)
def create_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        new_user_orm = service.create(db, user)
        new_user_response = UsuarioResponseConPersonal.model_validate(new_user_orm)
        return api_response_ok(new_user_response)
    except ValueError as e:
        return api_response_bad_request(str(e))
    except Exception as e:
        return api_response_bad_request("Error al crear el usuario")

@router.put("/{user_id}", response_model=UsuarioResponseConPersonal)
def update_user(user_id: int, user_update: UsuarioUpdate, db: Session = Depends(get_db)):
    try:
        user = service.update(db, user_id, user_update)
        if user is None:
            return api_response_not_found("Usuario no encontrado")
        response_user = UsuarioResponseConPersonal.model_validate(user)
        return api_response_ok(response_user)
    except ValueError as e:
        return api_response_bad_request(str(e))

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, user_id)
    if not deleted:
        return api_response_not_found("Usuario no encontrado")
    return api_response_ok({"detail": "Usuario eliminado"})
