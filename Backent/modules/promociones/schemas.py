from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class TipoPromocionEnum(str, Enum):
    DESCUENTO = "DESCUENTO"
    COMBO = "COMBO"
    LIQUIDACION = "LIQUIDACION"
    TEMPORADA = "TEMPORADA"
    LANZAMIENTO = "LANZAMIENTO"

class EstadoPromocionEnum(str, Enum):
    SUGERIDA = "SUGERIDA"
    ACTIVA = "ACTIVA"
    PAUSADA = "PAUSADA"
    FINALIZADA = "FINALIZADA"
    CANCELADA = "CANCELADA"

# Schemas para productos en combo
class ProductoComboBase(BaseModel):
    id_producto: int
    cantidad: int = 1
    descuento_individual: float = 0

class ProductoComboCreate(ProductoComboBase):
    pass

class ProductoComboResponse(ProductoComboBase):
    id: int
    nombre_producto: Optional[str] = None

    class Config:
        from_attributes = True

# Schemas principales de Promoción
class PromocionBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=255)
    descripcion: Optional[str] = None
    tipo_promocion: TipoPromocionEnum = TipoPromocionEnum.DESCUENTO
    id_producto: Optional[int] = None
    porcentaje_descuento: float = Field(default=0, ge=0, le=100)
    precio_promocional: Optional[float] = None
    cantidad_minima: int = Field(default=1, ge=1)
    fecha_inicio: date
    fecha_fin: date
    motivo: Optional[str] = None

class PromocionCreate(PromocionBase):
    codigo_promocion: Optional[str] = None  # Se genera automáticamente si no se proporciona
    productos_combo: Optional[List[ProductoComboCreate]] = None

class PromocionUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    tipo_promocion: Optional[TipoPromocionEnum] = None
    estado: Optional[EstadoPromocionEnum] = None
    id_producto: Optional[int] = None
    porcentaje_descuento: Optional[float] = Field(None, ge=0, le=100)
    precio_promocional: Optional[float] = None
    cantidad_minima: Optional[int] = Field(None, ge=1)
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    motivo: Optional[str] = None
    productos_combo: Optional[List[ProductoComboCreate]] = None

class PromocionResponse(PromocionBase):
    id_promocion: int
    codigo_promocion: str
    estado: EstadoPromocionEnum
    dias_hasta_vencimiento: Optional[int] = None
    ahorro_potencial: float = 0
    veces_aplicada: int = 0
    fecha_creacion: datetime
    fecha_modificacion: datetime
    creado_automaticamente: bool = False
    anulado: bool = False
    
    # Información del producto relacionado
    nombre_producto: Optional[str] = None
    stock_producto: Optional[float] = None
    precio_original: Optional[float] = None
    
    # Productos del combo
    productos_combo: Optional[List[ProductoComboResponse]] = None

    class Config:
        from_attributes = True

# Schema para sugerencias automáticas
class SugerenciaPromocion(BaseModel):
    id_producto: int
    nombre_producto: str
    stock_actual: float
    precio_venta: float
    dias_hasta_vencimiento: int
    tipo_sugerido: TipoPromocionEnum
    titulo_sugerido: str
    descripcion_sugerida: str
    descuento_sugerido: float
    ahorro_potencial: float
    urgencia: str  # "ALTA", "MEDIA", "BAJA"
    productos_combo_sugeridos: Optional[List[dict]] = None

class ActivarPromocionRequest(BaseModel):
    """Request para activar una promoción sugerida"""
    id_producto: int
    tipo_promocion: TipoPromocionEnum
    porcentaje_descuento: float
    fecha_inicio: date
    fecha_fin: date
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    productos_combo: Optional[List[ProductoComboCreate]] = None

class EstadisticasPromociones(BaseModel):
    total_promociones: int
    promociones_activas: int
    promociones_sugeridas: int
    ahorro_total_estimado: float
    productos_por_vencer: int
