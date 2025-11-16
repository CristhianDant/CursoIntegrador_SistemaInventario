from sqlalchemy import Column, BIGINT, VARCHAR , BOOLEAN
from database import Base

class Rol(Base):
    __tablename__ = 'roles'

    id_rol = Column(BIGINT, primary_key=True, autoincrement=True)
    nombre_rol = Column(VARCHAR(255), unique=True, nullable=False)
    descripcion = Column(VARCHAR(255), nullable=True)
    anulado = Column(BOOLEAN, nullable=False, default=0)