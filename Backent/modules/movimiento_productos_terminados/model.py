from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from modules.productos_terminados.model import ProductoTerminado
from modules.Gestion_Usuarios.usuario.model import Usuario
import datetime

class MovimientoProductoTerminado(Base):
    __tablename__ = 'movimiento_productos_terminados'

    id_movimiento = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_movimiento = Column(String(50), unique=True, nullable=False)
    id_producto = Column(BigInteger, ForeignKey('productos_terminados.id_producto'), nullable=False)
    tipo_movimiento = Column(String(20), nullable=False)
    motivo = Column(String(100), nullable=False)
    cantidad = Column(DECIMAL(12, 4), nullable=False)
    precio_venta = Column(DECIMAL(12, 4), default=0)
    fecha_movimiento = Column(TIMESTAMP, default=datetime.datetime.now)
    id_user = Column(BigInteger, ForeignKey('usuario.id_user'), nullable=False)
    id_documento_origen = Column(BigInteger)
    tipo_documento_origen = Column(String(50))
    observaciones = Column(Text)
    anulado = Column(BOOLEAN, default=False)

    producto = relationship("ProductoTerminado")
    usuario = relationship("Usuario")

