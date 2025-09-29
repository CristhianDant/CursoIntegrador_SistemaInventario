from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .service import ProveedorService
from . import schemas
from database import get_db
from utils.standard_responses import api_response_ok, api_response_bad_request, api_response_internal_server_error, api_response_not_found

router = APIRouter()

def get_proveedor_service(db: Session = Depends(get_db)) -> ProveedorService:
    return ProveedorService(db)

@router.post("/")
def create_proveedor(proveedor: schemas.ProveedorCreate, service: ProveedorService = Depends(get_proveedor_service)):
    try:
        new_proveedor = service.create_proveedor(proveedor=proveedor)
        return api_response_ok(data=new_proveedor)
    except HTTPException as e:
        if e.status_code == 400:
            return api_response_bad_request(error_message=e.detail)
        return api_response_internal_server_error(error_message=e.detail)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.get("/")
def read_proveedores(skip: int = 0, limit: int = 100, service: ProveedorService = Depends(get_proveedor_service)):
    try:
        proveedores = service.get_proveedores(skip=skip, limit=limit)
        return api_response_ok(data=proveedores)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.get("/{proveedor_id}")
def read_proveedor(proveedor_id: int, service: ProveedorService = Depends(get_proveedor_service)):
    try:
        db_proveedor = service.get_proveedor(proveedor_id=proveedor_id)
        return api_response_ok(data=db_proveedor)
    except HTTPException as e:
        if e.status_code == 404:
            return api_response_not_found(error_message=e.detail)
        return api_response_bad_request(error_message=e.detail)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.put("/{proveedor_id}")
def update_proveedor(proveedor_id: int, proveedor: schemas.ProveedorUpdate, service: ProveedorService = Depends(get_proveedor_service)):
    try:
        updated_proveedor = service.update_proveedor(proveedor_id=proveedor_id, proveedor=proveedor)
        return api_response_ok(data=updated_proveedor)
    except HTTPException as e:
        if e.status_code == 404:
            return api_response_not_found(error_message=e.detail)
        if e.status_code == 400:
            return api_response_bad_request(error_message=e.detail)
        return api_response_internal_server_error(error_message=e.detail)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.delete("/{proveedor_id}")
def delete_proveedor(proveedor_id: int, service: ProveedorService = Depends(get_proveedor_service)):
    try:
        deleted_proveedor = service.delete_proveedor(proveedor_id=proveedor_id)
        return api_response_ok(data=deleted_proveedor)
    except HTTPException as e:
        if e.status_code == 404:
            return api_response_not_found(error_message=e.detail)
        return api_response_internal_server_error(error_message=e.detail)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

