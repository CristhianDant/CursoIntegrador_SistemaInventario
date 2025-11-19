from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from modules.insumo.model import Insumo
from modules.Gestion_Usuarios.usuario.model import Usuario
import datetime

class MovimientoInsumo(Base):
    __tablename__ = 'movimiento_insumos'

    id_movimiento = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_movimiento = Column(String(50), unique=True, nullable=False)
    id_insumo = Column(BigInteger, ForeignKey('insumo.id_insumo'), nullable=False)
    tipo_movimiento = Column(String(20), nullable=False)
    motivo = Column(String(100), nullable=False)
    cantidad = Column(DECIMAL(12, 4), nullable=False)
    stock_anterior = Column(DECIMAL(12, 4), nullable=False)
    stock_nuevo = Column(DECIMAL(12, 4), nullable=False)
    fecha_movimiento = Column(TIMESTAMP, default=datetime.datetime.now)
    id_user = Column(BigInteger, ForeignKey('usuario.id_user'), nullable=False)
    id_documento_origen = Column(BigInteger)
    tipo_documento_origen = Column(String(50))
    observaciones = Column(Text)
    anulado = Column(BOOLEAN, default=False)

    insumo = relationship("Insumo")
    usuario = relationship("Usuario")

