from fastapi import FastAPI
from utils.logging_config import setup_logging
from modules.empresa import router as empresa_router
from modules.proveedores import router as proveedores_router
from modules.insumo import router as insumo_router

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

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
