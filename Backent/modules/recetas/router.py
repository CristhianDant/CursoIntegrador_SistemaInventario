from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from modules.recetas.schemas import Receta, RecetaCreate, RecetaUpdate
from modules.recetas.service import RecetaService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()

service = RecetaService()

@router.get("/", response_model=List[Receta])
def get_all_recetas(db: Session = Depends(get_db)):
    recetas = service.get_all(db)
    return api_response_ok(recetas)

@router.get("/{receta_id}", response_model=Receta)
def get_receta_by_id(receta_id: int, db: Session = Depends(get_db)):
    try:
        receta = service.get_by_id(db, receta_id)
        return api_response_ok(receta)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

@router.post("/", response_model=Receta)
def create_receta(receta: RecetaCreate, db: Session = Depends(get_db)):
    try:
        new_receta = service.create(db, receta)
        return api_response_ok(new_receta)
    except Exception as e:
        return api_response_bad_request(str(e))

@router.put("/{receta_id}", response_model=Receta)
def update_receta(receta_id: int, receta: RecetaUpdate, db: Session = Depends(get_db)):
    try:
        updated_receta = service.update(db, receta_id, receta)
        return api_response_ok(updated_receta)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))

@router.delete("/{receta_id}")
def delete_receta(receta_id: int, db: Session = Depends(get_db)):
    try:
        response = service.delete(db, receta_id)
        return api_response_ok(response)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

