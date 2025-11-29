from sqlalchemy import Column, BIGINT, VARCHAR, TEXT, TIMESTAMP, INTEGER
from sqlalchemy.sql import func
from database import Base


class ColaEmail(Base):
    """
    Tabla para almacenar emails pendientes de envío.
    Cuando no hay conexión a internet, los emails se encolan aquí
    y se procesan cuando la conexión se restablece.
    """
    __tablename__ = 'cola_email'

    id_email = Column(BIGINT, primary_key=True, autoincrement=True)
    destinatario = Column(VARCHAR(255), nullable=False)
    asunto = Column(VARCHAR(500), nullable=False)
    cuerpo_html = Column(TEXT, nullable=False)
    estado = Column(VARCHAR(50), nullable=False, default='PENDIENTE')  # PENDIENTE, ENVIADO, ERROR
    intentos = Column(INTEGER, nullable=False, default=0)
    ultimo_error = Column(TEXT, nullable=True)
    fecha_creacion = Column(TIMESTAMP, nullable=False, server_default=func.now())
    fecha_envio = Column(TIMESTAMP, nullable=True)
