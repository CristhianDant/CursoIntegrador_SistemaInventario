from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference , Layout
from contextlib import asynccontextmanager
import asyncio
from loguru import logger

from utils.logging_config import setup_logging
from modules.empresa import router as empresa_router
from modules.proveedores import router as proveedores_router
from modules.insumo import router as insumo_router
from modules.productos_terminados import router as productos_terminados_router
from modules.Gestion_Usuarios.usuario import router as usuario_router
from modules.Gestion_Usuarios.roles import router as roles_router
from modules.Gestion_Usuarios.permisos import router as permisos_router
from modules.Gestion_Usuarios.login import router as login_router
from modules.recetas import router as recetas_router
from modules.orden_de_compra import router as orden_de_compra_router
from modules.gestion_almacen_inusmos.ingresos_insumos import router as ingresos_productos_router
from modules.calidad_desperdicio_merma import router as merma_router
from modules.gestion_almacen_inusmos.movimiento_insumos import router as movimiento_insumos_router
from modules.movimiento_productos_terminados import router as movimiento_productos_terminados_router
from modules.gestion_almacen_inusmos.produccion import router as produccion_router
from modules.email_service import router as email_router
from modules.email_service.service import EmailService
from modules.promociones import promocion_router
from database import SessionLocal

# Configurar el logging antes de crear la aplicación
setup_logging()

# Intervalo en segundos para procesar la cola de emails (5 minutos = 300 segundos)
EMAIL_QUEUE_INTERVAL = 300
# Intervalo cuando no hay emails pendientes (1 hora para no consumir recursos)
EMAIL_QUEUE_IDLE_INTERVAL = 3600
# Días después de los cuales se eliminan los emails enviados/error
EMAIL_CLEANUP_DAYS = 1

async def procesar_cola_emails_periodicamente():
    """
    Tarea en segundo plano que procesa la cola de emails pendientes.
    - Si hay emails pendientes: revisa cada 5 minutos
    - Si no hay emails pendientes: revisa cada 30 minutos (modo idle)
    - Limpia emails antiguos (enviados/error) después de 1 día
    """
    email_service = EmailService()
    
    while True:
        try:
            # Crear sesión de base de datos
            db = SessionLocal()
            try:
                # Limpiar emails antiguos (enviados o con error de más de 1 día)
                eliminados = email_service.limpiar_emails_antiguos(db, dias=EMAIL_CLEANUP_DAYS)
                if eliminados > 0:
                    logger.info(f"🗑️ Limpieza: {eliminados} emails antiguos eliminados")
                
                # Verificar si hay emails pendientes
                stats = email_service.get_estadisticas(db)
                
                if stats['pendientes'] > 0:
                    logger.info(f"📧 Procesando cola de emails: {stats['pendientes']} pendientes")
                    resultado = email_service.procesar_cola(db)
                    logger.info(f"📧 Cola procesada: {resultado['enviados']} enviados, {resultado['fallidos']} fallidos")
                    
                    # Si aún hay pendientes, esperar intervalo corto
                    if resultado['fallidos'] > 0:
                        await asyncio.sleep(EMAIL_QUEUE_INTERVAL)
                    else:
                        # Todos enviados, pasar a modo idle
                        logger.info("📧 Cola vacía, pasando a modo idle (30 min)")
                        await asyncio.sleep(EMAIL_QUEUE_IDLE_INTERVAL)
                else:
                    # No hay pendientes, modo idle (revisa menos frecuente)
                    await asyncio.sleep(EMAIL_QUEUE_IDLE_INTERVAL)
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error en el scheduler de emails: {e}")
            await asyncio.sleep(EMAIL_QUEUE_INTERVAL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manejador del ciclo de vida de la aplicación.
    Inicia tareas en segundo plano al arrancar y las detiene al cerrar.
    """
    # Startup: iniciar tarea de procesamiento de cola de emails
    logger.info("🚀 Iniciando scheduler de cola de emails (cada 5 minutos)")
    task = asyncio.create_task(procesar_cola_emails_periodicamente())
    
    yield  # La aplicación se ejecuta aquí
    
    # Shutdown: cancelar la tarea
    logger.info("🛑 Deteniendo scheduler de cola de emails")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="API de Inventario",
    description="API RESTful para gestionar un sistema de inventario.",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de los módulos
app.include_router(empresa_router.router, prefix="/api/v1/empresas", tags=["Empresas"])
app.include_router(proveedores_router.router, prefix="/api/v1/proveedores", tags=["Proveedores"])
app.include_router(insumo_router.router, prefix="/api/v1/insumos", tags=["Insumos"])
app.include_router(productos_terminados_router.router, prefix="/api/v1/productos_terminados", tags=["Productos Terminados"])
app.include_router(usuario_router.router, prefix="/api/v1/usuarios", tags=["Usuarios"])
app.include_router(roles_router.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(permisos_router.router, prefix="/api/v1/permisos", tags=["Permisos"])
app.include_router(login_router.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(recetas_router.router, prefix="/api/v1/recetas", tags=["Recetas"])
app.include_router(orden_de_compra_router.router, prefix="/api/v1/ordenes_compra", tags=["Órdenes de Compra"])
app.include_router(ingresos_productos_router.router, prefix="/api/v1/ingresos_productos", tags=["Ingresos de Productos"])
app.include_router(merma_router.router, prefix="/api/v1/mermas", tags=["Mermas"])
app.include_router(movimiento_insumos_router.router, prefix="/api/v1/movimientos_insumos", tags=["Movimientos de Insumos"])
app.include_router(movimiento_productos_terminados_router.router, prefix="/api/v1/movimientos_productos_terminados", tags=["Movimientos de Productos Terminados"])
app.include_router(produccion_router.router, prefix="/api/v1/produccion", tags=["Produccion"])
app.include_router(email_router.router, prefix="/api/v1/emails", tags=["Emails"])
app.include_router(promocion_router, prefix="/api", tags=["Promociones"])


@app.get("/")
def read_root():
    return {"Hello": "World"}

# ------------- Documentación con Scalar -------------
@app.get("/docs-scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Documentación!!!",
        layout=Layout.MODERN,          # Diseño moderno
        dark_mode=True,                # Tema oscuro activado
        show_sidebar=True,             # Barra lateral con las rutas
        default_open_all_tags=True,    # Abrir todos los grupos de rutas
        hide_download_button=False,    # Permitir descargar el esquema
        hide_models=False,             # Mostrar los modelos de datos
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
