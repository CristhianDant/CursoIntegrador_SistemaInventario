from sqlalchemy import Column, BigInteger, String, Text, DECIMAL, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime


class Produccion(Base):
    """
    Modelo para la tabla de producción.
    Registra cada orden de producción ejecutada basada en una receta.
    """
    __tablename__ = 'produccion'

    id_produccion = Column(BigInteger, primary_key=True, autoincrement=True)
    numero_produccion = Column(String(50), unique=True, nullable=False)
    id_receta = Column(BigInteger, ForeignKey('recetas.id_receta'), nullable=False)
    cantidad_batch = Column(DECIMAL(12, 4), nullable=False)
    fecha_produccion = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now)
    id_user = Column(BigInteger, ForeignKey('usuario.id_user'), nullable=False)
    observaciones = Column(Text)
    anulado = Column(BOOLEAN, nullable=False, default=False)

    # Relaciones
    receta = relationship("Receta", back_populates="producciones")
    usuario = relationship("Usuario")
