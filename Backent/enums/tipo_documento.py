import enum

class TipoDocumentoEnum(str, enum.Enum):
    FACTURA = "FACTURA"
    BOLETA = "BOLETA"
    GUIA_REMISION = "GUIA_REMISION"

