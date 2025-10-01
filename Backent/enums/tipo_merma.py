import enum

class TipoMermaEnum(str, enum.Enum):
    VENCIMIENTO = "VENCIMIENTO"
    HONGEADO = "HONGEADO"
    DAÑO = "DAÑO"


