from sqlalchemy import Column, BIGINT, VARCHAR, Enum as SQLAlchemyEnum
from database import Base
from enums.tipo_modulo import TipoModulo

class Permiso(Base):
    __tablename__ = 'permisos'

    id_permiso = Column(BIGINT, primary_key=True, autoincrement=True)
    modulo = Column(SQLAlchemyEnum(TipoModulo), nullable=False)
    accion = Column(VARCHAR(255), nullable=False)

