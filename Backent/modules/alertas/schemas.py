from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


# ==================== ENUMS ====================

class TipoAlertaEnum(str, Enum):
    STOCK_CRITICO = "STOCK_CRITICO"
    VENCIMIENTO_PROXIMO = "VENCIMIENTO_PROXIMO"
    USAR_HOY = "USAR_HOY"
    VENCIDO = "VENCIDO"


class SemaforoEstadoEnum(str, Enum):
    VERDE = "VERDE"
    AMARILLO = "AMARILLO"
    ROJO = "ROJO"


# ==================== NOTIFICACIONES ====================

class NotificacionBase(BaseModel):
    tipo: TipoAlertaEnum
    titulo: str
    mensaje: str
    id_insumo: Optional[int] = None
    id_ingreso_detalle: Optional[int] = None
    semaforo: Optional[SemaforoEstadoEnum] = None
    dias_restantes: Optional[int] = None
    cantidad_afectada: Optional[str] = None


class NotificacionCreate(NotificacionBase):
    pass


class NotificacionResponse(NotificacionBase):
    id_notificacion: int
    leida: bool
    activa: bool
    fecha_creacion: datetime
    fecha_lectura: Optional[datetime] = None
    
    # Datos del insumo relacionado (para mostrar en UI)
    nombre_insumo: Optional[str] = None
    codigo_insumo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class NotificacionMarcarLeida(BaseModel):
    id_notificacion: int


# ==================== SEMÁFORO DE VENCIMIENTOS ====================

class InsumoSemaforo(BaseModel):
    """Representa un insumo con su estado de semáforo."""
    id_insumo: int
    codigo: str
    nombre: str
    unidad_medida: str
    cantidad_disponible: float
    fecha_vencimiento: date
    dias_restantes: int
    semaforo: SemaforoEstadoEnum
    accion_sugerida: str  # "Normal", "Usar esta semana", "Usar hoy"
    
    # Datos del lote
    id_ingreso_detalle: int
    numero_lote: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ResumenSemaforo(BaseModel):
    """Resumen del semáforo de vencimientos."""
    fecha_consulta: date
    total_verde: int
    total_amarillo: int
    total_rojo: int
    total_vencidos: int
    items_rojo: List[InsumoSemaforo]
    items_amarillo: List[InsumoSemaforo]

    model_config = ConfigDict(from_attributes=True)


# ==================== STOCK CRÍTICO ====================

class InsumoStockCritico(BaseModel):
    """Representa un insumo con stock crítico."""
    id_insumo: int
    codigo: str
    nombre: str
    unidad_medida: str
    stock_actual: float
    stock_minimo: float
    deficit: float
    es_critico: bool  # True si stock_actual = 0
    porcentaje_stock: float  # (stock_actual / stock_minimo) * 100

    model_config = ConfigDict(from_attributes=True)


class ResumenStockCritico(BaseModel):
    """Resumen de insumos con stock crítico."""
    fecha_consulta: date
    total_sin_stock: int      # stock_actual = 0
    total_bajo_minimo: int    # 0 < stock_actual < stock_minimo
    total_normal: int         # stock_actual >= stock_minimo
    items: List[InsumoStockCritico]

    model_config = ConfigDict(from_attributes=True)


# ==================== USAR HOY (FEFO) ====================

class ItemUsarHoy(BaseModel):
    """Item que debe usarse hoy siguiendo FEFO."""
    id_insumo: int
    codigo: str
    nombre: str
    unidad_medida: str
    cantidad_disponible: float
    fecha_vencimiento: date
    dias_restantes: int
    prioridad: int  # 1 = más urgente
    
    # Datos del lote
    id_ingreso_detalle: int
    numero_lote: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ListaUsarHoy(BaseModel):
    """Lista de items a usar hoy."""
    fecha: date
    total_items: int
    valor_estimado_en_riesgo: float
    items: List[ItemUsarHoy]

    model_config = ConfigDict(from_attributes=True)


# ==================== CONFIGURACIÓN DE ALERTAS ====================

class ConfiguracionAlertasBase(BaseModel):
    dias_verde: int = 15
    dias_amarillo: int = 7
    dias_rojo: int = 3
    hora_job: str = "06:00"
    email_alertas: Optional[str] = None


class ConfiguracionAlertasUpdate(ConfiguracionAlertasBase):
    pass


class ConfiguracionAlertasResponse(ConfiguracionAlertasBase):
    id_empresa: int

    model_config = ConfigDict(from_attributes=True)


# ==================== EJECUCIÓN DE JOB ====================

class JobEjecutarResponse(BaseModel):
    """Respuesta de la ejecución manual del job."""
    success: bool
    message: str
    alertas_vencimiento_creadas: int
    alertas_stock_creadas: int
    emails_encolados: int
    tiempo_ejecucion_ms: int

    model_config = ConfigDict(from_attributes=True)


# ==================== RESUMEN DE ALERTAS ====================

class ResumenAlertas(BaseModel):
    """Resumen general de alertas activas."""
    fecha: date
    total_no_leidas: int
    por_tipo: dict  # {"STOCK_CRITICO": 5, "USAR_HOY": 3, ...}
    ultima_ejecucion_job: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
