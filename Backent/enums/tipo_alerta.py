import enum


class TipoAlertaEnum(str, enum.Enum):
    """Tipos de alertas del sistema de inventario."""
    STOCK_CRITICO = "STOCK_CRITICO"          # Stock por debajo del mínimo
    VENCIMIENTO_PROXIMO = "VENCIMIENTO_PROXIMO"  # Vence en los próximos días (amarillo)
    USAR_HOY = "USAR_HOY"                    # Vence hoy o mañana (rojo)
    VENCIDO = "VENCIDO"                      # Ya venció
