from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .service import EmpresaService
from . import schemas
from database import get_db
from utils.standard_responses import api_response_ok, api_response_bad_request, api_response_internal_server_error, api_response_not_found

router = APIRouter()

def get_empresa_service(db: Session = Depends(get_db)) -> EmpresaService:
    return EmpresaService(db)

@router.post("/")
def create_empresa(empresa: schemas.EmpresaCreate, service: EmpresaService = Depends(get_empresa_service)):
    try:
        new_empresa = service.create_empresa(empresa=empresa)
        return api_response_ok(data=new_empresa)
    except HTTPException as e:
        if e.status_code == 400:
            return api_response_bad_request(error_message=e.detail)
        return api_response_internal_server_error(error_message=e.detail)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.get("/")
def read_empresas(skip: int = 0, limit: int = 100, service: EmpresaService = Depends(get_empresa_service)):
    try:
        empresas = service.get_empresas(skip=skip, limit=limit)
        return api_response_ok(data=empresas)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.get("/{empresa_id}")
def read_empresa(empresa_id: int, service: EmpresaService = Depends(get_empresa_service)):
    try:
        db_empresa = service.get_empresa(empresa_id=empresa_id)
        return api_response_ok(data=db_empresa)
    except HTTPException as e:
        if e.status_code == 404:
            return api_response_not_found(error_message=e.detail)
        return api_response_bad_request(error_message=e.detail)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.put("/{empresa_id}")
def update_empresa(empresa_id: int, empresa: schemas.EmpresaUpdate, service: EmpresaService = Depends(get_empresa_service)):
    try:
        updated_empresa = service.update_empresa(empresa_id=empresa_id, empresa=empresa)
        return api_response_ok(data=updated_empresa)
    except HTTPException as e:
        if e.status_code == 404:
            return api_response_not_found(error_message=e.detail)
        if e.status_code == 400:
            return api_response_bad_request(error_message=e.detail)
        return api_response_internal_server_error(error_message=e.detail)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))

@router.delete("/{empresa_id}")
def delete_empresa(empresa_id: int, service: EmpresaService = Depends(get_empresa_service)):
    try:
        deleted_empresa = service.delete_empresa(empresa_id=empresa_id)
        return api_response_ok(data=deleted_empresa)
    except HTTPException as e:
        if e.status_code == 404:
            return api_response_not_found(error_message=e.detail)
        return api_response_internal_server_error(error_message=e.detail)
    except Exception as e:
        return api_response_internal_server_error(error_message=str(e))
