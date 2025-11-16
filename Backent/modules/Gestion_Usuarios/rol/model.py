from sqlalchemy import Column, BIGINT, VARCHAR, BOOLEAN
from database import Base

class Rol(Base):
    __tablename__ = 'rol'

    id_rol = Column(BIGINT, primary_key=True, autoincrement=True)
    nombre_rol = Column(VARCHAR(255), nullable=False, unique=True)
    anulado = Column(BOOLEAN, nullable=False, default=False)

