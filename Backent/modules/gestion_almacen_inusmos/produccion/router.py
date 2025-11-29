from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from modules.gestion_almacen_inusmos.produccion.schemas import (
    ProduccionRequest,
    ValidacionStockResponse,
    ProduccionResponse,
    HistorialProduccionResponse,
    TrazabilidadProduccionResponse
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


@router.get("/historial", response_model=HistorialProduccionResponse)
def get_historial_producciones(
    limit: int = Query(50, ge=1, le=100, description="Cantidad de registros a obtener"),
    offset: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el historial de producciones realizadas.
    
    - **limit**: Cantidad máxima de registros a retornar (default: 50, max: 100)
    - **offset**: Cantidad de registros a saltar para paginación
    
    Retorna lista de producciones ordenadas por fecha descendente, con:
    - Datos de la producción (número, fecha, cantidad)
    - Datos de la receta utilizada
    - Datos del producto terminado generado
    - Usuario que ejecutó la producción
    """
    try:
        historial = service.get_historial_producciones(db, limit, offset)
        return api_response_ok(historial)
    except Exception as e:
        return api_response_bad_request(str(e))


@router.get("/trazabilidad/{id_produccion}", response_model=TrazabilidadProduccionResponse)
def get_trazabilidad_produccion(id_produccion: int, db: Session = Depends(get_db)):
    """
    Obtiene la trazabilidad completa de una producción específica.
    
    - **id_produccion**: ID de la producción a consultar
    
    Retorna información detallada de:
    - **Producción**: Número, fecha, cantidad batch, usuario
    - **Receta**: Código, nombre, rendimiento
    - **Producto terminado**: Nombre, movimiento de entrada, stock resultante
    - **Insumos consumidos**: Lista de lotes usados en orden FEFO con:
      - Número de movimiento
      - Insumo y lote
      - Fecha de vencimiento del lote
      - Cantidad consumida
      - Stock antes/después
    
    Permite rastrear exactamente qué lotes de insumos se usaron en cada producción.
    """
    try:
        trazabilidad = service.get_trazabilidad_produccion(db, id_produccion)
        return api_response_ok(trazabilidad)
    except HTTPException as e:
        if e.status_code == 404:
            return api_response_not_found(str(e.detail))
        return api_response_bad_request(str(e.detail))
    except Exception as e:
        return api_response_bad_request(str(e))
