from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from modules.insumo import service
from modules.insumo.schemas import Insumo, InsumoCreate, InsumoUpdate
from database import get_db
from utils.standard_responses import api_response_ok, api_response_bad_request, api_response_internal_server_error, api_response_not_found

router = APIRouter(
    prefix="/insumos",
    tags=["insumos"]
)

@router.post("/")
def create_insumo(insumo: InsumoCreate, db: Session = Depends(get_db)):
    try:
        new_insumo = service.create_insumo(db=db, insumo=insumo)
        return api_response_ok(data=new_insumo)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.get("/")
def read_insumos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        insumos = service.get_insumos(db, skip=skip, limit=limit)
        return api_response_ok(data=insumos)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.get("/{insumo_id}")
def read_insumo(insumo_id: int, db: Session = Depends(get_db)):
    try:
        db_insumo = service.get_insumo(db, insumo_id=insumo_id)
        if db_insumo is None:
            return api_response_not_found(error_message="Insumo not found")
        return api_response_ok(data=db_insumo)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.put("/{insumo_id}")
def update_insumo(insumo_id: int, insumo: InsumoUpdate, db: Session = Depends(get_db)):
    try:
        db_insumo = service.update_insumo(db, insumo_id=insumo_id, insumo=insumo)
        if db_insumo is None:
            return api_response_not_found(error_message="Insumo not found")
        return api_response_ok(data=db_insumo)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.delete("/{insumo_id}")
def delete_insumo(insumo_id: int, db: Session = Depends(get_db)):
    try:
        db_insumo = service.delete_insumo(db, insumo_id=insumo_id)
        if db_insumo is None:
            return api_response_not_found(error_message="Insumo not found")
        return api_response_ok(data=db_insumo)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))
