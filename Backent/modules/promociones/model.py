from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, DECIMAL, INT, TIMESTAMP, BOOLEAN, Enum as SQLEnum, ForeignKey, DATE
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from enum import Enum

class TipoPromocion(str, Enum):
    DESCUENTO = "DESCUENTO"           # Descuento directo por porcentaje
    COMBO = "COMBO"                   # Combinación de productos
    LIQUIDACION = "LIQUIDACION"       # Liquidación urgente por vencimiento
    TEMPORADA = "TEMPORADA"           # Promoción de temporada
    LANZAMIENTO = "LANZAMIENTO"       # Promoción de lanzamiento de producto

class EstadoPromocion(str, Enum):
    SUGERIDA = "SUGERIDA"             # Generada automáticamente, pendiente de activar
    ACTIVA = "ACTIVA"                 # Promoción activa
    PAUSADA = "PAUSADA"               # Temporalmente pausada
    FINALIZADA = "FINALIZADA"         # Terminó por fecha
    CANCELADA = "CANCELADA"           # Cancelada manualmente

class Promocion(Base):
    __tablename__ = 'promociones'

    id_promocion = Column(BIGINT, primary_key=True, autoincrement=True)
    
    # Información básica
    codigo_promocion = Column(VARCHAR(50), unique=True, nullable=False)
    titulo = Column(VARCHAR(255), nullable=False)
    descripcion = Column(TEXT)
    
    # Tipo y estado
    tipo_promocion = Column(SQLEnum(TipoPromocion), nullable=False, default=TipoPromocion.DESCUENTO)
    estado = Column(SQLEnum(EstadoPromocion), nullable=False, default=EstadoPromocion.SUGERIDA)
    
    # Producto principal (puede ser nulo para promociones generales)
    id_producto = Column(BIGINT, ForeignKey('productos_terminados.id_producto'), nullable=True)
    
    # Configuración de la promoción
    porcentaje_descuento = Column(DECIMAL(5, 2), default=0)  # Ej: 15.00 para 15%
    precio_promocional = Column(DECIMAL(12, 2), nullable=True)  # Precio fijo opcional
    cantidad_minima = Column(INT, default=1)  # Cantidad mínima para aplicar
    
    # Fechas
    fecha_inicio = Column(DATE, nullable=False)
    fecha_fin = Column(DATE, nullable=False)
    
    # Motivo de la promoción (para sugerencias automáticas)
    dias_hasta_vencimiento = Column(INT, nullable=True)  # Días hasta que vence el producto
    motivo = Column(TEXT)  # Explicación de por qué se sugiere
    
    # Métricas
    ahorro_potencial = Column(DECIMAL(12, 2), default=0)  # Ahorro estimado vs pérdida por merma
    veces_aplicada = Column(INT, default=0)  # Contador de uso
    
    # Auditoría
    fecha_creacion = Column(TIMESTAMP, nullable=False, server_default=func.now())
    fecha_modificacion = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    creado_automaticamente = Column(BOOLEAN, default=False)  # True si fue generada por el sistema
    anulado = Column(BOOLEAN, nullable=False, default=False)

    # Relaciones
    producto = relationship("ProductoTerminado", backref="promociones")
    productos_combo = relationship("PromocionCombo", back_populates="promocion", cascade="all, delete-orphan")


class PromocionCombo(Base):
    """Tabla intermedia para promociones tipo COMBO que incluyen múltiples productos"""
    __tablename__ = 'promociones_combo'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    id_promocion = Column(BIGINT, ForeignKey('promociones.id_promocion'), nullable=False)
    id_producto = Column(BIGINT, ForeignKey('productos_terminados.id_producto'), nullable=False)
    cantidad = Column(INT, default=1)
    descuento_individual = Column(DECIMAL(5, 2), default=0)  # Descuento específico para este producto en el combo

    # Relaciones
    promocion = relationship("Promocion", back_populates="productos_combo")
    producto = relationship("ProductoTerminado")
