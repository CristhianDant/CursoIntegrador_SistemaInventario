from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from modules.gestion_almacen_inusmos.produccion.schemas import (
    ProduccionRequest,
    ValidacionStockResponse,
    ProduccionResponse
)
from modules.gestion_almacen_inusmos.produccion.service import ProduccionService
from utils.standard_responses import api_response_ok, api_response_not_found, api_response_bad_request

router = APIRouter()

service = ProduccionService()


@router.post("/validar-stock", response_model=ValidacionStockResponse)
def validar_stock_produccion(id_receta: int, cantidad_batch: float, db: Session = Depends(get_db)):
    """
    Valida si hay stock suficiente para producir una receta.
    
    - **id_receta**: ID de la receta a producir
    - **cantidad_batch**: Cantidad de unidades/rendimientos a producir
    
    Retorna:
    - Lista de insumos requeridos con stock disponible
    - Indicador de si se puede producir o no
    - Mensaje descriptivo
    
    Este endpoint NO modifica datos, solo consulta.
    """
    try:
        from decimal import Decimal
        validacion = service.validar_stock_receta(db, id_receta, Decimal(str(cantidad_batch)))
        return api_response_ok(validacion)
    except HTTPException as e:
        return api_response_not_found(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))


@router.post("/ejecutar", response_model=ProduccionResponse)
def ejecutar_produccion(request: ProduccionRequest, db: Session = Depends(get_db)):
    """
    Ejecuta la producción de una receta, descontando insumos en orden FEFO.
    
    - **id_receta**: ID de la receta a producir
    - **cantidad_batch**: Cantidad de unidades/rendimientos a producir
    - **id_user**: ID del usuario que ejecuta la producción
    - **observaciones**: Observaciones opcionales
    
    Proceso:
    1. Valida que exista stock suficiente para TODOS los insumos
    2. Descuenta insumos de los lotes más próximos a vencer (FEFO)
    3. Crea movimientos de SALIDA en el Kardex
    
    Si falla algún insumo, se revierten TODOS los cambios.
    
    Retorna mensaje de éxito con información de la producción.
    """
    try:
        resultado = service.ejecutar_produccion(db, request)
        return api_response_ok(resultado)
    except HTTPException as e:
        if e.status_code == 404:
            return api_response_not_found(str(e.detail))
        return api_response_bad_request(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))
