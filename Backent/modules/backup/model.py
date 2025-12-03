"""
Modelo para el historial de backups del sistema.
"""

from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP, Boolean, Float
from sqlalchemy.sql import func
from database import Base


class HistorialBackup(Base):
    """
    Modelo para almacenar el historial de backups realizados.
    Permite trazabilidad y gestión de los archivos de respaldo.
    """
    __tablename__ = "historial_backup"

    id_backup = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Tipo de backup
    tipo = Column(String(20), nullable=False, index=True)  # 'COMPLETO' o 'DIFERENCIAL'
    
    # Información del archivo
    nombre_archivo = Column(String(255), nullable=False)
    ruta_archivo = Column(Text, nullable=False)
    tamanio_bytes = Column(BigInteger, nullable=True)  # Tamaño en bytes
    tamanio_legible = Column(String(50), nullable=True)  # Ej: "15.5 MB"
    
    # Estado
    estado = Column(String(20), nullable=False, default='COMPLETADO')  # COMPLETADO, ERROR, EN_PROCESO
    mensaje_error = Column(Text, nullable=True)
    
    # Métricas
    duracion_segundos = Column(Float, nullable=True)
    tablas_respaldadas = Column(BigInteger, nullable=True)
    registros_totales = Column(BigInteger, nullable=True)
    
    # Hash para verificación de integridad
    hash_md5 = Column(String(32), nullable=True)
    
    # Referencia al backup base (para diferenciales)
    id_backup_base = Column(BigInteger, nullable=True)  # FK al backup completo base
    
    # Auditoría
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    fecha_eliminacion = Column(TIMESTAMP(timezone=True), nullable=True)
    eliminado = Column(Boolean, default=False, index=True)
    
    # Ejecutado por
    ejecutado_por = Column(String(100), nullable=True)  # 'SCHEDULER', 'MANUAL', usuario
    
    def __repr__(self):
        return f"<HistorialBackup {self.id_backup}: {self.tipo} - {self.nombre_archivo}>"
