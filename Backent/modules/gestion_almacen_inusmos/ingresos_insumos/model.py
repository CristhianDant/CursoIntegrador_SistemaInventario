from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from modules.orden_de_compra.model import OrdenDeCompra
from modules.Gestion_Usuarios.usuario.model import Usuario
from modules.proveedores.model import Proveedor
from modules.insumo.model import Insumo
import datetime

class IngresoProducto(Base):
    __tablename__ = 'ingresos_insumos'

    id_ingreso = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_ingreso = Column(String(50), unique=True, nullable=False)
    id_orden_compra = Column(BigInteger, ForeignKey('orden_de_compra.id_orden'), nullable=True)
    numero_documento = Column(String(50), nullable=False)
    tipo_documento = Column(String(20), nullable=False)
    fecha_registro = Column(TIMESTAMP, default=datetime.datetime.now)
    fecha_ingreso = Column(TIMESTAMP, nullable=False)
    fecha_documento = Column(TIMESTAMP, nullable=False)
    id_user = Column(BigInteger, ForeignKey('usuario.id_user'), nullable=False)
    id_proveedor = Column(BigInteger, ForeignKey('proveedores.id_proveedor'), nullable=False)
    observaciones = Column(Text)
    estado = Column(String(20), nullable=False, default='COMPLETADO')
    monto_total = Column(DECIMAL(12, 2), default=0)
    anulado = Column(BOOLEAN, default=False)

    orden_compra = relationship("OrdenDeCompra")
    usuario = relationship("Usuario")
    proveedor = relationship("Proveedor")
    detalles = relationship("IngresoProductoDetalle", back_populates="ingreso")

class IngresoProductoDetalle(Base):
    __tablename__ = 'ingresos_insumos_detalle'

    id_ingreso_detalle = Column(BigInteger, primary_key=True, autoincrement=True)
    id_ingreso = Column(BigInteger, ForeignKey('ingresos_insumos.id_ingreso'), nullable=False)
    id_insumo = Column(BigInteger, ForeignKey('insumo.id_insumo'), nullable=False)
    cantidad_ingresada = Column(DECIMAL(12, 4), nullable=False)
    precio_unitario = Column(DECIMAL(12, 4), nullable=False)
    subtotal = Column(DECIMAL(12, 2), nullable=False)
    fecha_vencimiento = Column(TIMESTAMP)
    cantidad_restante = Column(DECIMAL(12, 4), nullable=False, default=0)

    ingreso = relationship("IngresoProducto", back_populates="detalles")
    insumo = relationship("Insumo")

