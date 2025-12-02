"""
Router para el módulo de Reportes.
Endpoints para análisis ABC, reporte diario, KPIs y rotación de inventario.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from loguru import logger

from database import get_db
from .service import ReportesService
from .schemas import (
    ReporteABCResponse,
    ReporteDiarioResponse,
    KPIsResponse,
    RotacionResponse
)

router = APIRouter()


def get_reportes_service(db: Session = Depends(get_db)) -> ReportesService:
    """Dependency injection para el servicio de reportes."""
    return ReportesService(db)


# ==================== ANÁLISIS ABC ====================

@router.get(
    "/abc",
    response_model=ReporteABCResponse,
    summary="Análisis ABC de productos",
    description="""
    Genera análisis ABC de productos basado en ventas del período.
    
    **Clasificación:**
    - **Categoría A (70% ventas):** Control DIARIO
    - **Categoría B (20% ventas):** Control SEMANAL  
    - **Categoría C (10% ventas):** Control MENSUAL
    
    **Parámetros obligatorios:**
    - `fecha_inicio`: Fecha de inicio del período (YYYY-MM-DD)
    - `fecha_fin`: Fecha de fin del período (YYYY-MM-DD)
    """
)
def obtener_reporte_abc(
    fecha_inicio: date = Query(..., description="Fecha de inicio del período"),
    fecha_fin: date = Query(..., description="Fecha de fin del período"),
    categoria: Optional[str] = Query(
        default=None,
        description="Filtrar por categoría de producto"
    ),
    service: ReportesService = Depends(get_reportes_service)
):
    """Genera análisis ABC de productos por ventas."""
    try:
        if fecha_fin < fecha_inicio:
            raise HTTPException(
                status_code=400,
                detail="fecha_fin debe ser mayor o igual a fecha_inicio"
            )
        
        return service.generar_reporte_abc(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            categoria=categoria
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar reporte ABC: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== REPORTE DIARIO ====================

@router.get(
    "/diario",
    response_model=ReporteDiarioResponse,
    summary="Reporte diario consolidado",
    description="""
    Genera reporte diario con:
    - Resumen de ventas (total, cantidad, por método de pago)
    - Resumen de mermas (cantidad, costo, % sobre ventas)
    - Resumen de producción (recetas producidas, cantidades)
    - Productos que vencen mañana
    - Stock crítico
    
    **Parámetro obligatorio:**
    - `fecha`: Fecha del reporte (YYYY-MM-DD)
    """
)
def obtener_reporte_diario(
    fecha: date = Query(..., description="Fecha del reporte"),
    service: ReportesService = Depends(get_reportes_service)
):
    """Genera reporte diario consolidado."""
    try:
        return service.generar_reporte_diario(fecha=fecha)
    except Exception as e:
        logger.error(f"Error al generar reporte diario: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== KPIs ====================

@router.get(
    "/kpis",
    response_model=KPIsResponse,
    summary="Dashboard de KPIs",
    description="""
    Obtiene todos los KPIs del sistema:
    
    | KPI | Meta | Unidad |
    |-----|------|--------|
    | Merma Diaria | < 3% | % |
    | Productos Vencidos Hoy | 0 | lotes |
    | Cumplimiento FEFO | > 95% | % |
    | Stock Crítico | < 3 | insumos |
    | Rotación Inventario | > 12 | veces/año |
    
    **Parámetro obligatorio:**
    - `fecha`: Fecha para calcular KPIs (YYYY-MM-DD)
    """
)
def obtener_kpis(
    fecha: date = Query(..., description="Fecha para calcular KPIs"),
    service: ReportesService = Depends(get_reportes_service)
):
    """Obtiene dashboard de KPIs."""
    try:
        return service.obtener_kpis(fecha=fecha)
    except Exception as e:
        logger.error(f"Error al obtener KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ROTACIÓN DE INVENTARIO ====================

@router.get(
    "/rotacion",
    response_model=RotacionResponse,
    summary="Análisis de rotación de inventario",
    description="""
    Genera análisis de rotación de inventario para insumos y productos terminados.
    
    **Fórmula:** Rotación = Consumo/Ventas del período / Stock promedio
    
    **Clasificación:**
    - **Alta:** ≥ 12 veces/año
    - **Media:** 6-12 veces/año
    - **Baja:** < 6 veces/año
    
    **Parámetros obligatorios:**
    - `fecha_inicio`: Fecha de inicio del período
    - `fecha_fin`: Fecha de fin del período
    
    **Paginación:**
    - `limit`: Máximo de registros por tipo (default: 100)
    - `offset`: Desplazamiento para paginación (default: 0)
    """
)
def obtener_reporte_rotacion(
    fecha_inicio: date = Query(..., description="Fecha de inicio del período"),
    fecha_fin: date = Query(..., description="Fecha de fin del período"),
    limit: int = Query(default=100, ge=1, le=500, description="Límite de registros"),
    offset: int = Query(default=0, ge=0, description="Desplazamiento"),
    service: ReportesService = Depends(get_reportes_service)
):
    """Genera análisis de rotación de inventario."""
    try:
        if fecha_fin < fecha_inicio:
            raise HTTPException(
                status_code=400,
                detail="fecha_fin debe ser mayor o igual a fecha_inicio"
            )
        
        return service.generar_reporte_rotacion(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            limit=limit,
            offset=offset
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al generar reporte de rotación: {e}")
        raise HTTPException(status_code=500, detail=str(e))
