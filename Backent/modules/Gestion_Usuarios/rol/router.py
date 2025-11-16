from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from .schemas import RolResponse, RolCreate, RolUpdate
from .service import RolService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()
service = RolService()

@router.get("/", response_model=List[RolResponse])
def get_all_roles(db: Session = Depends(get_db)):
    roles = service.get_all(db)
    return api_response_ok(roles)

@router.get("/{rol_id}", response_model=RolResponse)
def get_rol_by_id(rol_id: int, db: Session = Depends(get_db)):
    rol = service.get_by_id(db, rol_id)
    if rol is None:
        return api_response_not_found("Rol no encontrado")
    return api_response_ok(rol)

@router.post("/", response_model=RolResponse, status_code=201)
def create_rol(rol: RolCreate, db: Session = Depends(get_db)):
    try:
        new_rol = service.create(db, rol)
        return api_response_ok(new_rol)
    except ValueError as e:
        return api_response_bad_request(str(e))

@router.put("/{rol_id}", response_model=RolResponse)
def update_rol(rol_id: int, rol_update: RolUpdate, db: Session = Depends(get_db)):
    rol = service.update(db, rol_id, rol_update)
    if rol is None:
        return api_response_not_found("Rol no encontrado")
    return api_response_ok(rol)

@router.delete("/{rol_id}")
def delete_rol(rol_id: int, db: Session = Depends(get_db)):
    deleted = service.delete(db, rol_id)
    if not deleted:
        return api_response_not_found("Rol no encontrado")
    return api_response_ok({"detail": "Rol eliminado"})

