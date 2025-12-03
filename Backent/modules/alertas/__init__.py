# Módulo de Alertas - Tareas CRON para vencimientos y stock crítico

# Importar modelos necesarios para que SQLAlchemy los registre correctamente
# Esto evita errores de "could not locate name" en las relaciones
from modules.insumo.model import Insumo
from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProducto, IngresoProductoDetalle
from modules.empresa.model import Empresa
from modules.recetas.model import Receta, RecetaDetalle
