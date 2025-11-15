from sqlalchemy import Column, BIGINT, VARCHAR, BOOLEAN, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Rol(Base):
    __tablename__ = 'roles'

    id_rol = Column(BIGINT, primary_key=True, autoincrement=True)
    nombre_rol = Column(VARCHAR(100), nullable=False, unique=True)
    descripcion_rol = Column(VARCHAR(255))
    anulado = Column(BOOLEAN, nullable=False, default=False)

class UsuarioRol(Base):
    __tablename__ = 'usuario_roles'

    id_user_rol = Column(BIGINT, primary_key=True, autoincrement=True)
    id_user = Column(BIGINT, ForeignKey('usuario.id_user'), nullable=False)
    id_rol = Column(BIGINT, ForeignKey('roles.id_rol'), nullable=False)
    fecha_asignacion = Column(TIMESTAMP, nullable=False, server_default=func.now())
    anulado = Column(BOOLEAN, nullable=False, default=False)

    usuario = relationship("Usuario")
    rol = relationship("Rol")

class RolPermiso(Base):
    __tablename__ = 'roles_permisos'

    id_rol_permiso = Column(BIGINT, primary_key=True, autoincrement=True)
    id_rol = Column(BIGINT, ForeignKey('roles.id_rol'), nullable=False)
    id_permiso = Column(BIGINT, ForeignKey('permisos.id_permiso'), nullable=False)
    fecha_asignacion = Column(TIMESTAMP, nullable=False, server_default=func.now())
    anulado = Column(BOOLEAN, nullable=False, default=False)

    rol = relationship("Rol")
    permiso = relationship("Permiso")

