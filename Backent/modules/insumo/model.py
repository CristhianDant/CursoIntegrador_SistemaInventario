from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, DECIMAL, TIMESTAMP, BOOLEAN, Enum
from database import Base
from enums.unidad_medida import UnidadMedidaEnum
import datetime

class Insumo(Base):
    __tablename__ = "insumo"

    id_insumo = Column(BIGINT, primary_key=True, index=True, autoincrement=True)
    codigo = Column(VARCHAR(50), unique=True, nullable=False)
    nombre = Column(VARCHAR(255), nullable=False)
    descripcion = Column(TEXT)
    unidad_medida = Column(Enum(UnidadMedidaEnum), nullable=False)
    stock_minimo = Column(DECIMAL(12, 4), nullable=False, default=0)
    perecible = Column(BOOLEAN, nullable=False, default=False)
    categoria = Column(VARCHAR(100))
    fecha_registro = Column(TIMESTAMP, nullable=False, default=lambda: datetime.datetime.now(datetime.UTC))
    anulado = Column(BOOLEAN, nullable=False, default=False)
