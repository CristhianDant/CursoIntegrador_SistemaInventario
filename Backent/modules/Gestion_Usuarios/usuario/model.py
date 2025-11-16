from sqlalchemy import Column, BIGINT, VARCHAR, BOOLEAN, TIMESTAMP
from sqlalchemy.sql import func
from database import Base

class Usuario(Base):
    __tablename__ = 'usuario'

    id_user = Column(BIGINT, primary_key=True, autoincrement=True)
    nombre = Column(VARCHAR(255), nullable=False)
    apellidos = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), unique=True, nullable=False)
    password = Column(VARCHAR(255), nullable=False)
    fecha_registro = Column(TIMESTAMP, nullable=False, server_default=func.now())
    ultimo_acceso = Column(TIMESTAMP)
    anulado = Column(BOOLEAN, nullable=False, default=False)

