from fastapi import FastAPI
from utils.logging_config import setup_logging
from modules.empresa import router as empresa_router
from modules.proveedores import router as proveedores_router
from modules.insumo import router as insumo_router
from modules.productos_terminados import router as productos_terminados_router
from modules.usuario import router as usuario_router
from modules.permisos import router as permisos_router
from modules.login import router as login_router

# Configurar el logging antes de crear la aplicación
setup_logging()

app = FastAPI(
    title="API de Inventario",
    description="API RESTful para gestionar un sistema de inventario.",
    version="1.0.0"
)

# Incluir los routers de los módulos
app.include_router(empresa_router.router, prefix="/api/v1/empresas", tags=["Empresas"])
app.include_router(proveedores_router.router, prefix="/api/v1/proveedores", tags=["Proveedores"])
app.include_router(insumo_router.router, prefix="/api/v1/insumos", tags=["Insumos"])
app.include_router(productos_terminados_router.router, prefix="/api/v1/productos_terminados", tags=["Productos Terminados"])
app.include_router(usuario_router.router, prefix="/api/v1/usuarios", tags=["Usuarios"])
app.include_router(permisos_router.router, prefix="/api/v1", tags=["Permisos"])
app.include_router(login_router.router, prefix="/api/v1", tags=["Autenticación"])

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
