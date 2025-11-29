from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from .service import EmailService
from .schemas import EmailResponse
from utils.standard_responses import api_response_ok, api_response_bad_request

router = APIRouter()
service = EmailService()


@router.get("/estadisticas")
def get_estadisticas(db: Session = Depends(get_db)):
    """Obtiene estadísticas de la cola de emails"""
    stats = service.get_estadisticas(db)
    return api_response_ok(stats)


@router.get("/pendientes", response_model=list[EmailResponse])
def get_pendientes(db: Session = Depends(get_db)):
    """Obtiene lista de emails pendientes de envío"""
    pendientes = service.get_pendientes(db)
    return api_response_ok([EmailResponse.model_validate(e) for e in pendientes])


@router.post("/procesar-cola")
def procesar_cola(db: Session = Depends(get_db)):
    """
    Procesa la cola de emails pendientes.
    Útil para ejecutar manualmente cuando se recupera la conexión.
    """
    try:
        resultados = service.procesar_cola(db)
        return api_response_ok(resultados)
    except Exception as e:
        return api_response_bad_request(f"Error al procesar cola: {str(e)}")
