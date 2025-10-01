import enum

class EstadoEnum(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    TERMINADO = "TERMINADO"
    ANULADO = "ANULADO"
    ACTIVA = "ACTIVA"
    REGISTRADO = "REGISTRADO"

