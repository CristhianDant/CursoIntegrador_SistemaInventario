from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from modules.usuario.schemas import Usuario, UsuarioCreate, UsuarioUpdate
from modules.usuario.service import UsuarioService

router = APIRouter()
service = UsuarioService()

@router.get("/", response_model=List[Usuario])
def get_all_users(db: Session = Depends(get_db)):
    return service.get_all(db)

@router.get("/{user_id}", response_model=Usuario)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = service.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.post("/", response_model=Usuario, status_code=201)
def create_user(user: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = service.get_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    return service.create(db, user)

@router.put("/{user_id}", response_model=Usuario)
def update_user(user_id: int, user_update: UsuarioUpdate, db: Session = Depends(get_db)):
    user = service.update(db, user_id, user_update)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return

