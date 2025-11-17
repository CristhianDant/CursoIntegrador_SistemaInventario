from sqlalchemy import Column, BIGINT, VARCHAR, Enum as SQLAlchemyEnum, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from enums.tipo_modulo import TipoModulo

# Definición de la tabla de asociación para romper la importación circular
roles_permisos_tabla = Table(
    'roles_permisos', Base.metadata,
    Column('id_rol_permiso', BIGINT, primary_key=True, autoincrement=True),
    Column('id_rol', BIGINT, ForeignKey('roles.id_rol'), nullable=False),
    Column('id_permiso', BIGINT, ForeignKey('permisos.id_permiso'), nullable=False)
)

class Permiso(Base):
    __tablename__ = 'permisos'

    id_permiso = Column(BIGINT, primary_key=True, autoincrement=True)
    modulo = Column(SQLAlchemyEnum(TipoModulo), nullable=False)
    accion = Column(VARCHAR(255), nullable=False)

    roles = relationship('Rol', secondary=roles_permisos_tabla, back_populates='permisos')
