from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, DECIMAL, BOOLEAN, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Personal(Base):
    __tablename__ = 'personal'

    id_personal = Column(BIGINT, primary_key=True, autoincrement=True)
    id_usuario = Column(BIGINT, ForeignKey('usuario.id_user', ondelete='CASCADE'), unique=True, nullable=False)
    nombre_completo = Column(VARCHAR(255), nullable=False)
    direccion = Column(TEXT, nullable=True)
    referencia = Column(TEXT, nullable=True)
    dni = Column(VARCHAR(20), unique=True, nullable=False)
    area = Column(VARCHAR(50), nullable=True)
    salario = Column(DECIMAL(12, 2), nullable=False, default=0)
    anulado = Column(BOOLEAN, nullable=False, default=False)
    fecha_registro = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relación 1:1 con Usuario
    usuario = relationship('Usuario', back_populates='personal', uselist=False)
