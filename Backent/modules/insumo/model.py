from sqlalchemy import Column, BigInteger, VARCHAR, TEXT, DECIMAL, TIMESTAMP, BOOLEAN
from sqlalchemy.sql import func
from database import Base

class Insumo(Base):
    __tablename__ = 'insumo'

    id_insumo = Column(BigInteger, primary_key=True, autoincrement=True)
    codigo = Column(VARCHAR(50), unique=True, nullable=False)
    nombre = Column(VARCHAR(255), nullable=False)
    descripcion = Column(TEXT)
    unidad_medida = Column(VARCHAR(50), nullable=False)
    stock_actual = Column(DECIMAL(12, 4), nullable=False, default=0)
    stock_minimo = Column(DECIMAL(12, 4), nullable=False, default=0)
    fecha_caducidad = Column(TIMESTAMP)
    perecible = Column(BOOLEAN, nullable=False, default=False)
    precio_promedio = Column(DECIMAL(12, 4), default=0)
    categoria = Column(VARCHAR(100))
    fecha_registro = Column(TIMESTAMP, nullable=False, server_default=func.now())
    anulado = Column(BOOLEAN, nullable=False, default=False)

