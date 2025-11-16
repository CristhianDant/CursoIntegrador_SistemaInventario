from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from .schemas import PermisoResponse, PermisoCreate, PermisoUpdate
from .service import PermisoService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()
service = PermisoService()

@router.get("/", response_model=List[PermisoResponse])
def get_all_permisos(db: Session = Depends(get_db)):
    permisos = service.get_all(db)
    return api_response_ok(permisos)

@router.get("/{permiso_id}", response_model=PermisoResponse)
def get_permiso_by_id(permiso_id: int, db: Session = Depends(get_db)):
    permiso = service.get_by_id(db, permiso_id)
    if permiso is None:
        return api_response_not_found("Permiso no encontrado")
    return api_response_ok(permiso)

@router.post("/", response_model=PermisoResponse, status_code=201)
def create_permiso(permiso: PermisoCreate, db: Session = Depends(get_db)):
    try:
        new_permiso_orm = service.create(db, permiso)
        new_permiso_response = PermisoResponse.model_validate(new_permiso_orm)
        return api_response_ok(new_permiso_response)
    except ValueError as e:
        return api_response_bad_request(str(e))
    except Exception as e:
        return api_response_bad_request("Error al crear el permiso")

@router.put("/{permiso_id}", response_model=PermisoResponse)
def update_permiso(permiso_id: int, permiso_update: PermisoUpdate, db: Session = Depends(get_db)):
    permiso = service.update(db, permiso_id, permiso_update)
    if permiso is None:
        return api_response_not_found("Permiso no encontrado")
    return api_response_ok(permiso)


