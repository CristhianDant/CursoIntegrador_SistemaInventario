from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Receta(Base):
    __tablename__ = 'recetas'

    id_receta = Column(BigInteger, primary_key=True, autoincrement=True)
    id_producto = Column(BigInteger, ForeignKey('productos_terminados.id_producto'), nullable=False)
    codigo_receta = Column(String(50), unique=True, nullable=False)
    nombre_receta = Column(String(255), nullable=False)
    descripcion = Column(Text)
    rendimiento_producto_terminado = Column(DECIMAL(12, 4), nullable=False)
    costo_estimado = Column(DECIMAL(12, 2), default=0)
    fecha_creacion = Column(TIMESTAMP, default=datetime.datetime.now)
    version = Column(DECIMAL(3, 1), default=1.0)
    estado = Column(String(20), default='ACTIVA')
    anulado = Column(BOOLEAN, default=False)

    # Relación con ProductoTerminado
    producto = relationship("ProductoTerminado", back_populates="recetas")
    # Relación con RecetaDetalle
    detalles = relationship("RecetaDetalle", back_populates="receta")

class RecetaDetalle(Base):
    __tablename__ = 'recetas_detalle'

    id_receta_detalle = Column(BigInteger, primary_key=True, autoincrement=True)
    id_receta = Column(BigInteger, ForeignKey('recetas.id_receta'), nullable=False)
    id_insumo = Column(BigInteger, ForeignKey('insumo.id_insumo'), nullable=False)
    cantidad = Column(DECIMAL(12, 4), nullable=False)
    costo_unitario = Column(DECIMAL(12, 4), default=0)
    costo_total = Column(DECIMAL(12, 2), default=0)
    es_opcional = Column(BOOLEAN, default=False)
    observaciones = Column(Text)

    # Relación con Receta
    receta = relationship("Receta", back_populates="detalles")
    # Relación con Insumo
    insumo = relationship("Insumo", back_populates="recetas_detalles")

