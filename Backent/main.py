from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.logging_config import setup_logging
from modules.empresa import router as empresa_router
from modules.proveedores import router as proveedores_router
from modules.insumo import router as insumo_router
from modules.productos_terminados import router as productos_terminados_router
from modules.usuario import router as usuario_router
from modules.permisos import router as permisos_router
from modules.login import router as login_router
from modules.recetas import router as recetas_router
from modules.orden_de_compra import router as orden_de_compra_router
from modules.ingresos_productos import router as ingresos_productos_router
from modules.calidad_desperdicio_merma import router as merma_router
from modules.movimiento_insumos import router as movimiento_insumos_router
from modules.movimiento_productos_terminados import router as movimiento_productos_terminados_router

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
app.include_router(permisos_router.router, prefix="/api/v1", tags=["Permisos"])
app.include_router(login_router.router, prefix="/api/v1", tags=["Autenticación"])
app.include_router(recetas_router.router, prefix="/api/v1/recetas", tags=["Recetas"])
app.include_router(orden_de_compra_router.router, prefix="/api/v1/ordenes_compra", tags=["Órdenes de Compra"])
app.include_router(ingresos_productos_router.router, prefix="/api/v1/ingresos_productos", tags=["Ingresos de Productos"])
app.include_router(merma_router.router, prefix="/api/v1/mermas", tags=["Mermas"])
app.include_router(movimiento_insumos_router.router, prefix="/api/v1/movimientos_insumos", tags=["Movimientos de Insumos"])
app.include_router(movimiento_productos_terminados_router.router, prefix="/api/v1/movimientos_productos_terminados", tags=["Movimientos de Productos Terminados"])


@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
