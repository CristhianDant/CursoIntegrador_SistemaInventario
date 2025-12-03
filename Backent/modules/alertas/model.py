from sqlalchemy import Column, BigInteger, String, Text, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

# Importar enums de Python (no se crean en BD, se validan en Python)
from enums.tipo_alerta import TipoAlertaEnum
from enums.semaforo_estado import SemaforoEstadoEnum


# Re-exportar para compatibilidad
TipoAlerta = TipoAlertaEnum
SemaforoEstado = SemaforoEstadoEnum


class Notificacion(Base):
    """
    Modelo para almacenar notificaciones/alertas del sistema.
    Generadas automáticamente por el job CRON diario.
    
    Los campos 'tipo' y 'semaforo' usan VARCHAR en BD y se validan
    con enums de Python (TipoAlertaEnum, SemaforoEstadoEnum).
    """
    __tablename__ = "notificaciones"

    id_notificacion = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Tipo y contenido (VARCHAR, validado con enum Python)
    tipo = Column(String(50), nullable=False, index=True)  # TipoAlertaEnum
    titulo = Column(String(200), nullable=False)
    mensaje = Column(Text, nullable=False)
    
    # Referencias opcionales (para trazabilidad)
    id_insumo = Column(BigInteger, ForeignKey('insumo.id_insumo'), nullable=True, index=True)
    id_ingreso_detalle = Column(BigInteger, ForeignKey('ingresos_insumos_detalle.id_ingreso_detalle'), nullable=True)
    
    # Metadatos adicionales (VARCHAR, validado con enum Python)
    semaforo = Column(String(20), nullable=True)  # SemaforoEstadoEnum
    dias_restantes = Column(BigInteger, nullable=True)
    cantidad_afectada = Column(String(50), nullable=True)
    
    # Estado de la notificación
    leida = Column(Boolean, default=False, index=True)
    activa = Column(Boolean, default=True, index=True)
    
    # Auditoría
    fecha_creacion = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    fecha_lectura = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relaciones - usando strings para evitar problemas de importación circular
    insumo = relationship("Insumo", foreign_keys=[id_insumo], lazy="select")
    ingreso_detalle = relationship("IngresoProductoDetalle", foreign_keys=[id_ingreso_detalle], lazy="select")
    
    def __repr__(self):
        return f"<Notificacion {self.id_notificacion}: {self.tipo} - {self.titulo}>"
