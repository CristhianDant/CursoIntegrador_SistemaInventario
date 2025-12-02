"""
Schemas para el módulo de Reportes.
Respuestas JSON directas para análisis ABC, reporte diario, KPIs y rotación.
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal


# ==================== ANÁLISIS ABC ====================

class ProductoABC(BaseModel):
    """Producto clasificado según análisis ABC."""
    id_producto: int
    codigo: str
    nombre: str
    cantidad_vendida: Decimal = Field(description="Unidades vendidas en el período")
    monto_total: Decimal = Field(description="Monto total de ventas")
    porcentaje_ventas: Decimal = Field(description="% sobre el total de ventas")
    porcentaje_acumulado: Decimal = Field(description="% acumulado")
    clasificacion: str = Field(description="A, B o C")
    frecuencia_control: str = Field(description="diario, semanal, mensual")
    
    model_config = ConfigDict(from_attributes=True)


class ReporteABCResponse(BaseModel):
    """Respuesta del análisis ABC de productos."""
    fecha_inicio: date
    fecha_fin: date
    total_ventas: Decimal
    total_productos: int
    
    # Resumen por categoría
    resumen: dict = Field(description="Conteo y % por categoría A, B, C")
    
    # Productos clasificados
    productos_a: List[ProductoABC] = Field(description="70% de ventas - Control DIARIO")
    productos_b: List[ProductoABC] = Field(description="20% de ventas - Control SEMANAL")
    productos_c: List[ProductoABC] = Field(description="10% de ventas - Control MENSUAL")


# ==================== REPORTE DIARIO ====================

class ResumenVentasDiario(BaseModel):
    """Resumen de ventas del día."""
    total_ventas: Decimal
    cantidad_transacciones: int
    ticket_promedio: Decimal
    ventas_por_metodo: dict = Field(description="Desglose por método de pago")


class ResumenMermasDiario(BaseModel):
    """Resumen de mermas del día."""
    cantidad_casos: int
    cantidad_total_kg: Decimal
    costo_total: Decimal
    porcentaje_sobre_ventas: Decimal
    meta_porcentaje: Decimal = Decimal("3.0")
    cumple_meta: bool
    desglose_por_tipo: dict = Field(description="Desglose por tipo de merma")


class ResumenProduccionDiario(BaseModel):
    """Resumen de producción del día."""
    total_producciones: int
    total_unidades_producidas: Decimal
    recetas_producidas: List[dict] = Field(description="Lista de recetas y cantidades")


class ItemVencimiento(BaseModel):
    """Item próximo a vencer."""
    id_insumo: int
    codigo: str
    nombre: str
    cantidad: Decimal
    unidad_medida: str
    fecha_vencimiento: date
    dias_restantes: int
    valor_estimado: Optional[Decimal] = None


class ItemStockCritico(BaseModel):
    """Item con stock crítico."""
    id_insumo: int
    codigo: str
    nombre: str
    stock_actual: Decimal
    stock_minimo: Decimal
    deficit: Decimal
    unidad_medida: str
    es_critico: bool = Field(description="True si stock = 0")


class ReporteDiarioResponse(BaseModel):
    """Respuesta del reporte diario consolidado."""
    fecha: date
    generado_en: datetime
    
    # Secciones
    ventas: ResumenVentasDiario
    mermas: ResumenMermasDiario
    produccion: ResumenProduccionDiario
    vencen_manana: List[ItemVencimiento]
    stock_critico: List[ItemStockCritico]


# ==================== KPIs ====================

class KPIValue(BaseModel):
    """Valor de un KPI individual."""
    nombre: str
    valor: Decimal
    unidad: str
    meta: Decimal
    cumple_meta: bool
    tendencia: Optional[str] = Field(default=None, description="subiendo, bajando, estable")
    detalle: Optional[str] = None


class KPIsResponse(BaseModel):
    """Respuesta con todos los KPIs del sistema."""
    fecha: date
    
    # KPIs individuales
    merma_diaria: KPIValue
    productos_vencidos_hoy: KPIValue
    cumplimiento_fefo: KPIValue
    stock_critico: KPIValue
    rotacion_inventario: KPIValue
    
    # Resumen general
    kpis_cumplidos: int
    kpis_totales: int
    porcentaje_cumplimiento: Decimal


# ==================== ROTACIÓN DE INVENTARIO ====================

class ItemRotacion(BaseModel):
    """Item con información de rotación."""
    id: int
    codigo: str
    nombre: str
    tipo: str = Field(description="insumo o producto_terminado")
    stock_actual: Decimal
    unidad_medida: str
    consumo_periodo: Decimal = Field(description="Cantidad consumida/vendida en el período")
    dias_stock: Decimal = Field(description="Días de stock restante al ritmo actual")
    rotacion_periodo: Decimal = Field(description="Veces que rota en el período")
    rotacion_anualizada: Decimal = Field(description="Rotación proyectada a 12 meses")
    clasificacion: str = Field(description="alta, media, baja")


class RotacionResponse(BaseModel):
    """Respuesta del análisis de rotación de inventario."""
    fecha_inicio: date
    fecha_fin: date
    dias_periodo: int
    
    # Resumen
    rotacion_promedio_anual: Decimal
    meta_rotacion_anual: Decimal = Decimal("12.0")
    cumple_meta: bool
    
    # Conteos
    total_items: int
    items_alta_rotacion: int
    items_media_rotacion: int
    items_baja_rotacion: int
    
    # Detalle
    insumos: List[ItemRotacion]
    productos_terminados: List[ItemRotacion]
    
    # Paginación
    limit: int
    offset: int
    total: int
