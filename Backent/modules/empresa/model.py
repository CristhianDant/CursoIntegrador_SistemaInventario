from sqlalchemy import Column, Integer, String, Boolean, text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


# Configuración por defecto para alertas
DEFAULT_CONFIGURACION_ALERTAS = {
    "dias_verde": 15,
    "dias_amarillo": 7,
    "dias_rojo": 3,
    "hora_job": "06:00",
    "email_alertas": None
}


class Empresa(Base):
    __tablename__ = "empresa"

    id_empresa = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String(255), nullable=False)
    ruc = Column(String(20), unique=True, nullable=False, index=True)
    direccion = Column(String, nullable=False)
    telefono = Column(String(20), nullable=False)
    email = Column(String(255), nullable=False)
    estado = Column(Boolean, nullable=False, server_default=text('true'))
    fecha_registro = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    configuracion_alertas = Column(JSONB, nullable=True, default=DEFAULT_CONFIGURACION_ALERTAS)

    def get_configuracion_alertas(self) -> dict:
        """Retorna la configuración de alertas o valores por defecto."""
        if self.configuracion_alertas:
            return self.configuracion_alertas
        return DEFAULT_CONFIGURACION_ALERTAS.copy()
