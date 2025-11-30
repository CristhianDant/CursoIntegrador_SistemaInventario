from sqlalchemy import Column, BIGINT, VARCHAR, TIMESTAMP, DECIMAL, TEXT, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Venta(Base):
    """
    Modelo para la tabla ventas.
    Registra las ventas realizadas en el sistema.
    """
    __tablename__ = "ventas"
    
    id_venta = Column(BIGINT, primary_key=True, autoincrement=True)
    numero_venta = Column(VARCHAR(50), unique=True, nullable=False)
    fecha_venta = Column(TIMESTAMP, nullable=False, server_default=func.now())
    total = Column(DECIMAL(12, 2), nullable=False)
    metodo_pago = Column(VARCHAR(20), nullable=False)  # efectivo, tarjeta, transferencia
    id_user = Column(BIGINT, ForeignKey('usuario.id_user', ondelete='RESTRICT'), nullable=False)
    observaciones = Column(TEXT, nullable=True)
    anulado = Column(BOOLEAN, nullable=False, server_default='false')
    
    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[id_user])
    detalles = relationship("VentaDetalle", back_populates="venta", cascade="all, delete-orphan")


class VentaDetalle(Base):
    """
    Modelo para la tabla venta_detalles.
    Detalle de productos vendidos en cada venta.
    """
    __tablename__ = "venta_detalles"
    
    id_detalle = Column(BIGINT, primary_key=True, autoincrement=True)
    id_venta = Column(BIGINT, ForeignKey('ventas.id_venta', ondelete='CASCADE'), nullable=False)
    id_producto = Column(BIGINT, ForeignKey('productos_terminados.id_producto', ondelete='RESTRICT'), nullable=False)
    cantidad = Column(DECIMAL(12, 4), nullable=False)
    precio_unitario = Column(DECIMAL(12, 2), nullable=False)
    descuento_porcentaje = Column(DECIMAL(5, 2), nullable=False, server_default='0')
    subtotal = Column(DECIMAL(12, 2), nullable=False)
    
    # Relaciones
    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("ProductoTerminado", foreign_keys=[id_producto])
