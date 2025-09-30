from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, DECIMAL, INT, TIMESTAMP, BOOLEAN
from sqlalchemy.sql import func
from database import Base

class ProductoTerminado(Base):
    __tablename__ = 'productos_terminados'

    id_producto = Column(BIGINT, primary_key=True, autoincrement=True)
    codigo_producto = Column(VARCHAR(50), unique=True, nullable=False)
    nombre = Column(VARCHAR(255), nullable=False)
    descripcion = Column(TEXT)
    unidad_medida = Column(VARCHAR(50), nullable=False)
    stock_actual = Column(DECIMAL(12, 4), nullable=False, default=0)
    stock_minimo = Column(DECIMAL(12, 4), nullable=False, default=0)
    vida_util_dias = Column(INT)
    precio_venta = Column(DECIMAL(12, 2), default=0)
    fecha_registro = Column(TIMESTAMP, nullable=False, server_default=func.now())
    anulado = Column(BOOLEAN, nullable=False, default=False)

