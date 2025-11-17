from sqlalchemy import Column, BIGINT, VARCHAR, BOOLEAN, TIMESTAMP, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# Tabla de asociación Usuario <-> Roles
usuario_roles_tabla = Table('usuario_roles', Base.metadata,
    Column('id_usuario_rol', BIGINT, primary_key=True, autoincrement=True),
    Column('id_user', BIGINT, ForeignKey('usuario.id_user'), nullable=False),
    Column('id_rol', BIGINT, ForeignKey('roles.id_rol'), nullable=False)
)

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

    # Relación con Roles
    roles = relationship('Rol', secondary=usuario_roles_tabla, back_populates='usuarios')
