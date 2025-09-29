from sqlalchemy import Column, BigInteger, String, Text, Boolean, TIMESTAMP, func
from database import Base

class Proveedor(Base):
    __tablename__ = "proveedores"

    id_proveedor = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    ruc_dni = Column(String(20), unique=True, nullable=False, index=True)
    numero_contacto = Column(String(15), nullable=False)
    email_contacto = Column(String(255), nullable=False)
    direccion_fiscal = Column(Text, nullable=False)
    fecha_registro = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    anulado = Column(Boolean, default=False, nullable=False)

