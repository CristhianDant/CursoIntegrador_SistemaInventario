import enum


class SemaforoEstadoEnum(str, enum.Enum):
    """Estados del semáforo de vencimiento para insumos."""
    VERDE = "VERDE"        # >dias_verde días de vida útil (normal)
    AMARILLO = "AMARILLO"  # dias_rojo-dias_verde días (usar esta semana)
    ROJO = "ROJO"          # <dias_rojo días (usar hoy/prioridad)
