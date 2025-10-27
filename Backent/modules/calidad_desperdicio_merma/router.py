from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from modules.calidad_desperdicio_merma.schemas import Merma, MermaCreate, MermaUpdate
from modules.calidad_desperdicio_merma.service import MermaService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()

service = MermaService()

@router.get("/", response_model=List[Merma])
def get_all_mermas(db: Session = Depends(get_db)):
    mermas = service.get_all(db)
    return api_response_ok(mermas)

@router.get("/{merma_id}", response_model=Merma)
def get_merma_by_id(merma_id: int, db: Session = Depends(get_db)):
    try:
        merma = service.get_by_id(db, merma_id)
        return api_response_ok(merma)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

@router.post("/", response_model=Merma)
def create_merma(merma: MermaCreate, db: Session = Depends(get_db)):
    try:
        new_merma = service.create(db, merma)
        return api_response_ok(new_merma)
    except Exception as e:
        return api_response_bad_request(str(e))

@router.put("/{merma_id}", response_model=Merma)
def update_merma(merma_id: int, merma: MermaUpdate, db: Session = Depends(get_db)):
    try:
        updated_merma = service.update(db, merma_id, merma)
        return api_response_ok(updated_merma)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))

@router.delete("/{merma_id}")
def delete_merma(merma_id: int, db: Session = Depends(get_db)):
    try:
        response = service.delete(db, merma_id)
        return api_response_ok(response)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))

