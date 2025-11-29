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
    Incluye información de la producción creada.
    """
    success: bool
    mensaje: str
    id_produccion: int
    numero_produccion: str
    id_receta: int
    nombre_receta: str
    cantidad_batch: Decimal
    cantidad_producida: Decimal  # cantidad_batch * rendimiento
    total_movimientos_creados: int  # Número de movimientos de salida creados

    class Config:
        from_attributes = True


# ===== Response Schemas para Historial =====

class HistorialProduccionItem(BaseModel):
    """Un item del historial de producciones"""
    id_produccion: int
    numero_produccion: str
    id_receta: int
    codigo_receta: str
    nombre_receta: str
    nombre_producto: str
    cantidad_batch: Decimal
    rendimiento_producto_terminado: Decimal
    cantidad_producida: Decimal
    fecha_produccion: datetime.datetime
    id_user: int
    nombre_usuario: str
    observaciones: Optional[str]
    anulado: bool

    class Config:
        from_attributes = True


class HistorialProduccionResponse(BaseModel):
    """Respuesta del historial de producciones"""
    total: int
    producciones: List[HistorialProduccionItem]

    class Config:
        from_attributes = True


# ===== Response Schemas para Trazabilidad =====

class InsumoConsumidoTrazabilidad(BaseModel):
    """Información de un lote de insumo consumido en la producción"""
    id_movimiento: int
    numero_movimiento: str
    id_insumo: int
    codigo_insumo: str
    nombre_insumo: str
    unidad_medida: str
    id_lote: int
    fecha_vencimiento_lote: Optional[datetime.datetime]
    cantidad_consumida: Decimal
    stock_anterior_lote: Optional[Decimal]
    stock_nuevo_lote: Optional[Decimal]
    fecha_movimiento: datetime.datetime

    class Config:
        from_attributes = True


class MovimientoProductoTerminado(BaseModel):
    """Información del movimiento de entrada del producto terminado"""
    id_movimiento: Optional[int]
    numero_movimiento: Optional[str]
    cantidad: Optional[Decimal]
    stock_anterior: Optional[Decimal]
    stock_nuevo: Optional[Decimal]
    fecha_movimiento: Optional[datetime.datetime]

    class Config:
        from_attributes = True


class ProduccionTrazabilidad(BaseModel):
    """Datos básicos de la producción para trazabilidad"""
    id_produccion: int
    numero_produccion: str
    fecha_produccion: datetime.datetime
    cantidad_batch: Decimal
    cantidad_producida: Decimal
    usuario: str
    observaciones: Optional[str]
    anulado: bool

    class Config:
        from_attributes = True


class RecetaTrazabilidad(BaseModel):
    """Datos de la receta usada en la producción"""
    id_receta: int
    codigo_receta: str
    nombre_receta: str
    rendimiento_producto_terminado: Decimal

    class Config:
        from_attributes = True


class ProductoTerminadoTrazabilidad(BaseModel):
    """Datos del producto terminado generado"""
    id_producto: int
    nombre_producto: str
    movimiento_entrada: Optional[MovimientoProductoTerminado]

    class Config:
        from_attributes = True


class TrazabilidadProduccionResponse(BaseModel):
    """
    Respuesta completa de trazabilidad de una producción.
    Incluye datos de producción, receta, lotes consumidos y producto generado.
    """
    produccion: ProduccionTrazabilidad
    receta: RecetaTrazabilidad
    producto_terminado: ProductoTerminadoTrazabilidad
    insumos_consumidos: List[InsumoConsumidoTrazabilidad]
    total_lotes_consumidos: int

    class Config:
        from_attributes = True
