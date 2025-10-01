from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from modules.insumo.model import Insumo
from modules.productos_terminados.model import ProductoTerminado
from modules.usuario.model import Usuario
import datetime

class CalidadDesperdicioMerma(Base):
    __tablename__ = 'calidad_desperdicio_merma'

    id_merma = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_registro = Column(String(50), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False)
    causa = Column(Text, nullable=False)
    cantidad = Column(DECIMAL(12, 4), nullable=False)
    costo_unitario = Column(DECIMAL(12, 4), default=0)
    costo_total = Column(DECIMAL(12, 2), default=0)
    fecha_caso = Column(TIMESTAMP, default=datetime.datetime.now)
    id_insumo = Column(BigInteger, ForeignKey('insumo.id_insumo'))
    id_producto = Column(BigInteger, ForeignKey('productos_terminados.id_producto'))
    id_user_responsable = Column(BigInteger, ForeignKey('usuario.id_user'), nullable=False)
    observacion = Column(Text)
    estado = Column(String(20), nullable=False, default='REGISTRADO')
    anulado = Column(BOOLEAN, default=False)

    insumo = relationship("Insumo")
    producto = relationship("ProductoTerminado")
    responsable = relationship("Usuario")

