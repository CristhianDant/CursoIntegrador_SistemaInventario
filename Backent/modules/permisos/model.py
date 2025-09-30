from sqlalchemy import Column, BIGINT, VARCHAR, BOOLEAN, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Permiso(Base):
    __tablename__ = 'permisos'

    id_permiso = Column(BIGINT, primary_key=True, autoincrement=True)
    descripcion_permiso = Column(VARCHAR(150), nullable=False)
    modulo = Column(VARCHAR(50), nullable=False)
    accion = Column(VARCHAR(50), nullable=False)

class UsuarioPermiso(Base):
    __tablename__ = 'usuario_permisos'

    id_user_permiso = Column(BIGINT, primary_key=True, autoincrement=True)
    id_user = Column(BIGINT, ForeignKey('usuario.id_user'), nullable=False)
    id_permiso = Column(BIGINT, ForeignKey('permisos.id_permiso'), nullable=False)
    fecha_asignacion = Column(TIMESTAMP, nullable=False, server_default=func.now())
    anulado = Column(BOOLEAN, nullable=False, default=False)

    usuario = relationship("Usuario")
    permiso = relationship("Permiso")

