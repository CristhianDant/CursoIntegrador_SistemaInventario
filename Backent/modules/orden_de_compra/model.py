from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from modules.proveedores.model import Proveedor
from modules.usuario.model import Usuario
from modules.insumo.model import Insumo
import datetime

class OrdenDeCompra(Base):
    __tablename__ = 'orden_de_compra'

    id_orden = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_orden = Column(String(50), unique=True, nullable=False)
    id_proveedor = Column(BigInteger, ForeignKey('proveedores.id_proveedor'), nullable=False)
    fecha_orden = Column(TIMESTAMP, default=datetime.datetime.now)
    fecha_entrega_esperada = Column(TIMESTAMP, nullable=False)
    moneda = Column(String(3), nullable=False, default='PEN')
    tipo_cambio = Column(DECIMAL(8, 4), default=1)
    sub_total = Column(DECIMAL(12, 2), nullable=False)
    descuento = Column(DECIMAL(12, 2), default=0)
    igv = Column(DECIMAL(12, 2), nullable=False, default=0)
    total = Column(DECIMAL(12, 2), nullable=False)
    estado = Column(String(20), nullable=False, default='PENDIENTE')
    observaciones = Column(Text)
    id_user_creador = Column(BigInteger, ForeignKey('usuario.id_user'), nullable=False)
    id_user_aprobador = Column(BigInteger, ForeignKey('usuario.id_user'))
    fecha_aprobacion = Column(TIMESTAMP)
    anulado = Column(BOOLEAN, default=False)

    proveedor = relationship("Proveedor")
    creador = relationship("Usuario", foreign_keys=[id_user_creador])
    aprobador = relationship("Usuario", foreign_keys=[id_user_aprobador])
    detalles = relationship("OrdenDeCompraDetalle", back_populates="orden_compra")

class OrdenDeCompraDetalle(Base):
    __tablename__ = 'orden_de_compra_detalle'

    id_orden_detalle = Column(BigInteger, primary_key=True, autoincrement=True)
    id_orden = Column(BigInteger, ForeignKey('orden_de_compra.id_orden'), nullable=False)
    id_insumo = Column(BigInteger, ForeignKey('insumo.id_insumo'), nullable=False)
    cantidad = Column(DECIMAL(12, 4), nullable=False)
    precio_unitario = Column(DECIMAL(12, 4), nullable=False)
    descuento_unitario = Column(DECIMAL(12, 4), default=0)
    sub_total = Column(DECIMAL(12, 2), nullable=False)
    observaciones = Column(Text)

    orden_compra = relationship("OrdenDeCompra", back_populates="detalles")
    insumo = relationship("Insumo")

