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
from modules.gestion_almacen_productos.movimiento_productos_terminados import router as movimiento_productos_terminados_router
from modules.gestion_almacen_inusmos.produccion import router as produccion_router
from modules.gestion_almacen_productos.ventas import router as ventas_router
from modules.email_service import router as email_router
from modules.email_service.service import EmailService
from modules.promociones import promocion_router
from database import SessionLocal

# Configurar el logging antes de crear la aplicación
setup_logging()

app = FastAPI(
    title="API de Inventario",
    description="API RESTful para gestionar un sistema de inventario.",
    version="1.0.0"
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
app.include_router(ventas_router.router, prefix="/api/v1/ventas", tags=["Ventas"])


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
