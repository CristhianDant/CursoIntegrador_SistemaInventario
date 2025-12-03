"""
Schemas para el módulo de backup.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TipoBackup(str, Enum):
    """Tipos de backup soportados."""
    COMPLETO = "COMPLETO"
    DIFERENCIAL = "DIFERENCIAL"


class EstadoBackup(str, Enum):
    """Estados posibles de un backup."""
    EN_PROCESO = "EN_PROCESO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"


# ==================== Request Schemas ====================

class BackupManualRequest(BaseModel):
    """Request para ejecutar un backup manual."""
    tipo: TipoBackup = Field(
        default=TipoBackup.COMPLETO,
        description="Tipo de backup a realizar"
    )
    incluir_datos: bool = Field(
        default=True,
        description="Incluir datos en el backup (False = solo estructura)"
    )


class EnviarBackupEmailRequest(BaseModel):
    """Request para enviar backup por email."""
    id_backup: int = Field(..., description="ID del backup a enviar")
    email_destino: str = Field(..., description="Email destino")
    mensaje: Optional[str] = Field(
        default=None,
        description="Mensaje adicional en el email"
    )


# ==================== Response Schemas ====================

class BackupResponse(BaseModel):
    """Response con información de un backup."""
    id_backup: int
    tipo: str
    nombre_archivo: str
    ruta_archivo: str
    tamanio_legible: Optional[str]
    estado: str
    mensaje_error: Optional[str]
    duracion_segundos: Optional[float]
    tablas_respaldadas: Optional[int]
    registros_totales: Optional[int]
    hash_md5: Optional[str]
    fecha_creacion: datetime
    ejecutado_por: Optional[str]
    
    class Config:
        from_attributes = True


class BackupListResponse(BaseModel):
    """Response con lista de backups."""
    total: int
    backups: List[BackupResponse]
    espacio_total_usado: str  # Ej: "150.5 MB"


class BackupResultado(BaseModel):
    """Resultado de una operación de backup."""
    exito: bool
    mensaje: str
    backup: Optional[BackupResponse] = None


class EstadisticasBackup(BaseModel):
    """Estadísticas del sistema de backups."""
    total_backups: int
    backups_completos: int
    backups_diferenciales: int
    espacio_usado_bytes: int
    espacio_usado_legible: str
    ultimo_backup_completo: Optional[datetime]
    ultimo_backup_diferencial: Optional[datetime]
    proxima_limpieza: Optional[datetime]
    dias_retencion: int


class LimpiezaResultado(BaseModel):
    """Resultado de la limpieza de backups antiguos."""
    backups_eliminados: int
    espacio_liberado_bytes: int
    espacio_liberado_legible: str
    archivos_eliminados: List[str]
