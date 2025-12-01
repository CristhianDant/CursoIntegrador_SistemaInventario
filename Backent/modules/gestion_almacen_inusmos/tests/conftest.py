"""
Fixtures y configuración para tests unitarios de gestión de almacén.
Tests con mocks - NO requiere base de datos real.
"""
import pytest
from unittest.mock import Mock, MagicMock
from decimal import Decimal
from datetime import datetime, date, timedelta


@pytest.fixture
def mock_db_session():
    """Mock de sesión de base de datos."""
    session = MagicMock()
    session.commit = Mock()
    session.rollback = Mock()
    session.refresh = Mock()
    session.add = Mock()
    session.query = Mock()
    return session


@pytest.fixture
def mock_receta_data():
    """Datos mock de una receta con sus insumos."""
    return {
        "receta": {
            "id_receta": 1,
            "codigo_receta": "REC001",
            "nombre_receta": "Pan Francés",
            "rendimiento_producto_terminado": Decimal("10.00")
        },
        "insumos": [
            {
                "id_insumo": 1,
                "codigo_insumo": "INS001",
                "nombre_insumo": "Harina de Trigo",
                "unidad_medida": "kg",
                "cantidad_por_rendimiento": Decimal("2.00"),
                "es_opcional": False
            },
            {
                "id_insumo": 2,
                "codigo_insumo": "INS002",
                "nombre_insumo": "Sal",
                "unidad_medida": "kg",
                "cantidad_por_rendimiento": Decimal("0.05"),
                "es_opcional": False
            }
        ]
    }


@pytest.fixture
def mock_lotes_fefo():
    """Datos mock de lotes FEFO."""
    return [
        {
            "id_ingreso_detalle": 1,
            "id_ingreso": 1,
            "cantidad_ingresada": Decimal("50.00"),
            "cantidad_restante": Decimal("50.00"),
            "precio_unitario": Decimal("2.50"),
            "subtotal": Decimal("125.00"),
            "fecha_vencimiento": date.today() + timedelta(days=180),
            "numero_ingreso": "ING-001",
            "fecha_ingreso": date.today(),
            "nombre_proveedor": "Proveedor Test S.A."
        },
        {
            "id_ingreso_detalle": 2,
            "id_ingreso": 2,
            "cantidad_ingresada": Decimal("30.00"),
            "cantidad_restante": Decimal("30.00"),
            "precio_unitario": Decimal("2.80"),
            "subtotal": Decimal("84.00"),
            "fecha_vencimiento": date.today() + timedelta(days=90),
            "numero_ingreso": "ING-002",
            "fecha_ingreso": date.today() - timedelta(days=10),
            "nombre_proveedor": "Proveedor Test S.A."
        }
    ]


@pytest.fixture
def mock_produccion_creada():
    """Datos mock de producción creada."""
    return {
        "id_produccion": 1,
        "numero_produccion": "PROD-20251201-001",
        "fecha_produccion": datetime.now()
    }


@pytest.fixture
def mock_insumo():
    """Mock de un insumo."""
    insumo = Mock()
    insumo.id_insumo = 1
    insumo.codigo = "INS001"
    insumo.nombre = "Harina de Trigo"
    insumo.unidad_medida = Mock(value="kg")
    insumo.anulado = False
    return insumo


@pytest.fixture
def mock_ingreso():
    """Mock de un ingreso de producto."""
    ingreso = Mock()
    ingreso.id_ingreso = 1
    ingreso.numero_ingreso = "ING-001"
    ingreso.fecha_ingreso = date.today()
    ingreso.monto_total = Decimal("118.00")
    ingreso.estado = "COMPLETADO"
    ingreso.anulado = False
    return ingreso


@pytest.fixture
def mock_movimiento():
    """Mock de un movimiento de insumo."""
    movimiento = Mock()
    movimiento.id_movimiento = 1
    movimiento.numero_movimiento = "MOV-001"
    movimiento.tipo_movimiento = "SALIDA"
    movimiento.cantidad = Decimal("10.00")
    movimiento.fecha_movimiento = datetime.now()
    return movimiento


@pytest.fixture
def mock_historial_producciones():
    """Datos mock de historial de producciones."""
    return [
        {
            "id_produccion": 1,
            "numero_produccion": "PROD-20251201-001",
            "id_receta": 1,
            "codigo_receta": "REC001",
            "nombre_receta": "Pan Francés",
            "nombre_producto": "Pan Francés",
            "cantidad_batch": Decimal("5.00"),
            "rendimiento_producto_terminado": Decimal("10.00"),
            "cantidad_producida": Decimal("50.00"),
            "fecha_produccion": datetime.now(),
            "id_user": 1,
            "nombre_usuario": "Usuario Test",
            "observaciones": "Producción de prueba",
            "anulado": False
        },
        {
            "id_produccion": 2,
            "numero_produccion": "PROD-20251201-002",
            "id_receta": 1,
            "codigo_receta": "REC001",
            "nombre_receta": "Pan Francés",
            "nombre_producto": "Pan Francés",
            "cantidad_batch": Decimal("3.00"),
            "rendimiento_producto_terminado": Decimal("10.00"),
            "cantidad_producida": Decimal("30.00"),
            "fecha_produccion": datetime.now() - timedelta(hours=2),
            "id_user": 1,
            "nombre_usuario": "Usuario Test",
            "observaciones": "Segunda producción",
            "anulado": False
        }
    ]


@pytest.fixture
def mock_trazabilidad_produccion():
    """Datos mock de trazabilidad de producción."""
    return {
        "produccion": {
            "id_produccion": 1,
            "numero_produccion": "PROD-20251201-001",
            "fecha_produccion": datetime.now(),
            "cantidad_batch": Decimal("5.00"),
            "cantidad_producida": Decimal("50.00"),
            "usuario": "Usuario Test",
            "observaciones": "Producción de prueba",
            "anulado": False
        },
        "receta": {
            "id_receta": 1,
            "codigo_receta": "REC001",
            "nombre_receta": "Pan Francés",
            "rendimiento_producto_terminado": Decimal("10.00")
        },
        "producto_terminado": {
            "id_producto": 1,
            "nombre_producto": "Pan Francés",
            "movimiento_entrada": {
                "id_movimiento": 1,
                "numero_movimiento": "MOV-PT-001",
                "cantidad": Decimal("50.00"),
                "fecha_movimiento": datetime.now()
            }
        },
        "insumos_consumidos": [
            {
                "id_movimiento": 1,
                "numero_movimiento": "MOV-INS-001",
                "id_insumo": 1,
                "codigo_insumo": "INS001",
                "nombre_insumo": "Harina de Trigo",
                "unidad_medida": "kg",
                "id_lote": 1,
                "fecha_vencimiento_lote": date.today() + timedelta(days=180),
                "cantidad_consumida": Decimal("10.00"),
                "stock_anterior_lote": Decimal("50.00"),
                "stock_nuevo_lote": Decimal("40.00"),
                "fecha_movimiento": datetime.now()
            }
        ],
        "total_lotes_consumidos": 1
    }
