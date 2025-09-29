from sqlalchemy import Column, Integer, String, Boolean, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from database import Base

class Empresa(Base):
    __tablename__ = "empresa"

    id_empresa = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String(255), nullable=False)
    ruc = Column(String(20), unique=True, nullable=False, index=True)
    direccion = Column(String, nullable=False)
    telefono = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    estado = Column(Boolean, nullable=False, server_default=text('true'))
    fecha_registro = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
