from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
import datetime


# ===== Request Schemas =====

class ProduccionRequest(BaseModel):
    """
    Request para ejecutar una producción basada en receta.
    El frontend envía la receta y la cantidad de batch a producir.
    """
    id_receta: int
    cantidad_batch: Decimal  # Número de "rendimientos" a producir
    id_user: int
    observaciones: Optional[str] = None


# ===== Response Schemas para Validación =====

class InsumoRequeridoResponse(BaseModel):
    """Información de un insumo requerido por la receta"""
    id_insumo: int
    codigo_insumo: str
    nombre_insumo: str
    unidad_medida: str
    cantidad_requerida: Decimal  # Cantidad total necesaria para el batch
    stock_disponible: Decimal    # Stock total disponible (suma de lotes)
    es_suficiente: bool          # True si stock_disponible >= cantidad_requerida

    class Config:
        from_attributes = True


class ValidacionStockResponse(BaseModel):
    """
    Respuesta de validación de stock antes de ejecutar producción.
    Indica si hay stock suficiente para todos los insumos.
    """
    id_receta: int
    nombre_receta: str
    cantidad_batch: Decimal
    puede_producir: bool  # True si TODOS los insumos tienen stock suficiente
    insumos: List[InsumoRequeridoResponse] = []
    mensaje: str

    class Config:
        from_attributes = True


# ===== Response Schema para Ejecución =====

class ProduccionResponse(BaseModel):
    """
    Respuesta después de ejecutar la producción.
    Mensaje simple indicando éxito.
    """
    success: bool
    mensaje: str
    id_receta: int
    nombre_receta: str
    cantidad_batch: Decimal
    total_movimientos_creados: int  # Número de movimientos de salida creados

    class Config:
        from_attributes = True
