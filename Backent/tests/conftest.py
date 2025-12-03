"""
Configuración de pruebas de integración con base de datos PostgreSQL de prueba.

Este archivo configura:
- Conexión a base de datos de prueba PostgreSQL (test_inventario)
- Fixtures para TestClient con override de dependencias
- Fixtures con datos base reutilizables (empresa, usuario admin, etc.)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Agregar el directorio padre al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, get_db
from main import app
from security.password_utils import get_password_hash

# ============================================================
# CONFIGURACIÓN DE BASE DE DATOS DE PRUEBA
# ============================================================

# Cargar configuración desde el módulo config
from config import settings

# URL de la base de datos de prueba PostgreSQL
# Usa las mismas credenciales que producción pero con base de datos diferente
# Asegúrate de crear la base de datos: CREATE DATABASE reposteria_test;
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    f"postgresql://{settings.POST_USER}:{settings.POST_PASS}@{settings.HOST_DB}:{settings.POST_PORT}/reposteria_test"
)

# Crear engine y session para pruebas
test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ============================================================
# FIXTURES DE BASE DE DATOS Y CLIENTE
# ============================================================

@pytest.fixture(scope="function")
def db_session():
    """
    Crea las tablas y proporciona una sesión de BD limpia para cada test.
    Al finalizar, elimina todas las tablas para asegurar aislamiento.
    """
    # Crear todas las tablas antes del test
    Base.metadata.create_all(bind=test_engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Eliminar todas las tablas después del test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Proporciona TestClient con la dependencia de BD sobrescrita.
    Usa la sesión de prueba en lugar de la sesión de producción.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpiar overrides después del test
    app.dependency_overrides.clear()


# ============================================================
# FIXTURES DE DATOS BASE REUTILIZABLES
# ============================================================

@pytest.fixture
def empresa_base(db_session):
    """
    Crea una empresa base para usar en los tests.
    Retorna el objeto empresa creado.
    """
    from modules.empresa.model import Empresa
    
    empresa = Empresa(
        nombre_empresa="Panadería Test S.A.C.",
        ruc="20123456789",
        direccion="Av. Prueba 123, Lima",
        telefono="01-1234567",
        email="test@panaderia.com",
        estado=True
    )
    db_session.add(empresa)
    db_session.commit()
    db_session.refresh(empresa)
    
    return empresa


@pytest.fixture
def usuario_admin(db_session):
    """
    Crea un usuario administrador para usar en los tests.
    La contraseña sin hash es: 'Admin123!'
    """
    from modules.Gestion_Usuarios.usuario.model import Usuario
    from modules.Gestion_Usuarios.roles.model import Rol
    
    # Primero crear el rol admin
    rol_admin = Rol(
        nombre_rol="admin",
        descripcion="Rol de administrador con acceso completo"
    )
    db_session.add(rol_admin)
    db_session.commit()
    
    # Crear usuario admin
    usuario = Usuario(
        nombre="Admin",
        apellidos="Test",
        email="admin@test.com",
        password=get_password_hash("Admin123!"),
        anulado=False
    )
    usuario.roles.append(rol_admin)
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(usuario)
    
    return usuario


@pytest.fixture
def proveedor_base(db_session):
    """
    Crea un proveedor base para usar en los tests.
    """
    from modules.proveedores.model import Proveedor
    
    proveedor = Proveedor(
        nombre="Proveedor Test S.A.",
        ruc_dni="20987654321",
        numero_contacto="999888777",
        email_contacto="proveedor@test.com",
        direccion_fiscal="Calle Proveedor 456, Lima",
        anulado=False
    )
    db_session.add(proveedor)
    db_session.commit()
    db_session.refresh(proveedor)
    
    return proveedor


@pytest.fixture
def producto_terminado_base(db_session):
    """
    Crea un producto terminado base para usar en los tests.
    """
    from modules.productos_terminados.model import ProductoTerminado
    from decimal import Decimal
    
    producto = ProductoTerminado(
        codigo_producto="PROD001",
        nombre="Pan Integral Test",
        descripcion="Pan integral para pruebas",
        unidad_medida="UNIDAD",
        stock_actual=Decimal("100.00"),
        stock_minimo=Decimal("10.00"),
        vida_util_dias=3,
        precio_venta=Decimal("5.00"),
        anulado=False
    )
    db_session.add(producto)
    db_session.commit()
    db_session.refresh(producto)
    
    return producto


@pytest.fixture
def producto_con_stock(db_session):
    """
    Crea un producto terminado con stock específico para tests de ventas.
    """
    from modules.productos_terminados.model import ProductoTerminado
    from decimal import Decimal
    
    producto = ProductoTerminado(
        codigo_producto="PROD002",
        nombre="Croissant Test",
        descripcion="Croissant para pruebas de venta",
        unidad_medida="UNIDAD",
        stock_actual=Decimal("50.00"),
        stock_minimo=Decimal("5.00"),
        vida_util_dias=2,
        precio_venta=Decimal("3.50"),
        anulado=False
    )
    db_session.add(producto)
    db_session.commit()
    db_session.refresh(producto)
    
    return producto


# ============================================================
# MARCADORES DE PYTEST
# ============================================================

def pytest_configure(config):
    """Configurar marcadores personalizados para pytest."""
    config.addinivalue_line(
        "markers", "integration: marca tests como pruebas de integración"
    )
