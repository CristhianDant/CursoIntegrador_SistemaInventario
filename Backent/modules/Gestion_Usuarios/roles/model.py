from sqlalchemy import Column, BIGINT, VARCHAR, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from modules.Gestion_Usuarios.permisos.model import Permiso, roles_permisos_tabla

class Rol(Base):
    __tablename__ = 'roles'

    id_rol = Column(BIGINT, primary_key=True, autoincrement=True)
    nombre_rol = Column(VARCHAR(255), unique=True, nullable=False)
    descripcion = Column(VARCHAR(255), nullable=True)
    anulado = Column(BOOLEAN, nullable=False, default=False)

    permisos = relationship('Permiso', secondary=roles_permisos_tabla, back_populates='roles')
