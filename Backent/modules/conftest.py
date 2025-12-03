"""
Fixtures compartidos para tests unitarios de servicios.

Este módulo contiene fixtures comunes que pueden ser utilizados
por todos los tests de los módulos del backend.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, date
from decimal import Decimal


# ==================== FIXTURES DE BASE DE DATOS ====================

@pytest.fixture
def mock_db_session():
    """
    Mock de sesión de base de datos SQLAlchemy.
    Incluye todos los métodos comunes utilizados en los repositorios.
    """
    session = MagicMock()
    session.commit = Mock()
    session.rollback = Mock()
    session.refresh = Mock()
    session.add = Mock()
    session.delete = Mock()
    session.flush = Mock()
    session.query = Mock(return_value=MagicMock())
    session.execute = Mock()
    session.begin = Mock()
    session.close = Mock()
    return session


# ==================== FIXTURES DE USUARIO ====================

@pytest.fixture
def mock_usuario():
    """Mock de un usuario básico."""
    usuario = MagicMock()
    usuario.id_user = 1
    usuario.email = "test@test.com"
    usuario.nombre = "Test"
    usuario.apellidos = "Usuario"
    usuario.password = "hashed_password"
    usuario.anulado = False
    usuario.roles = []
    usuario.personal = None
    return usuario


@pytest.fixture
def mock_rol():
    """Mock de un rol."""
    rol = MagicMock()
    rol.id_rol = 1
    rol.nombre = "Admin"
    rol.descripcion = "Administrador del sistema"
    rol.anulado = False
    rol.permisos = []
    return rol


@pytest.fixture
def mock_permiso():
    """Mock de un permiso."""
    permiso = MagicMock()
    permiso.id_permiso = 1
    permiso.codigo = "USERS_READ"
    permiso.descripcion = "Leer usuarios"
    permiso.id_modulo = 1
    permiso.anulado = False
    return permiso


# ==================== FIXTURES DE PRODUCTOS E INSUMOS ====================

@pytest.fixture
def mock_insumo():
    """Mock de un insumo."""
    insumo = MagicMock()
    insumo.id_insumo = 1
    insumo.codigo = "INS001"
    insumo.nombre = "Insumo Test"
    insumo.unidad_medida = "KG"
    insumo.categoria = "MATERIAS_PRIMAS"
    insumo.stock_actual = Decimal("100.00")
    insumo.stock_minimo = Decimal("10.00")
    insumo.anulado = False
    return insumo


@pytest.fixture
def mock_producto_terminado():
    """Mock de un producto terminado."""
    producto = MagicMock()
    producto.id_producto = 1
    producto.codigo_producto = "PROD001"
    producto.nombre = "Producto Test"
    producto.descripcion = "Descripción del producto"
    producto.unidad_medida = "KG"
    producto.stock_actual = Decimal("50.00")
    producto.stock_minimo = Decimal("5.00")
    producto.precio_venta = Decimal("25.50")
    producto.precio_costo = Decimal("15.00")
    producto.vida_util_dias = 7
    producto.fecha_registro = datetime.now()
    producto.anulado = False
    return producto


# ==================== FIXTURES DE PROVEEDORES Y COMPRAS ====================

@pytest.fixture
def mock_proveedor():
    """Mock de un proveedor."""
    proveedor = MagicMock()
    proveedor.id_proveedor = 1
    proveedor.ruc = "20123456789"
    proveedor.razon_social = "Proveedor Test S.A.C."
    proveedor.nombre_comercial = "Proveedor Test"
    proveedor.direccion = "Av. Test 123"
    proveedor.telefono = "999999999"
    proveedor.email = "proveedor@test.com"
    proveedor.anulado = False
    return proveedor


@pytest.fixture
def mock_orden_compra():
    """Mock de una orden de compra."""
    orden = MagicMock()
    orden.id_orden = 1
    orden.numero_orden = "OC-2025-0001"
    orden.id_proveedor = 1
    orden.fecha_orden = datetime.now()
    orden.fecha_entrega_esperada = datetime.now()
    orden.moneda = "PEN"
    orden.tipo_cambio = Decimal("1")
    orden.sub_total = Decimal("100.00")
    orden.descuento = Decimal("0")
    orden.igv = Decimal("18.00")
    orden.total = Decimal("118.00")
    orden.estado = "PENDIENTE"
    orden.observaciones = None
    orden.id_user_creador = 1
    orden.anulado = False
    orden.detalles = []
    return orden


# ==================== FIXTURES DE ALERTAS Y NOTIFICACIONES ====================

@pytest.fixture
def mock_notificacion():
    """Mock de una notificación."""
    notificacion = MagicMock()
    notificacion.id_notificacion = 1
    notificacion.tipo = "STOCK_CRITICO"
    notificacion.titulo = "Stock bajo"
    notificacion.mensaje = "El insumo X está bajo mínimo"
    notificacion.id_insumo = 1
    notificacion.id_ingreso_detalle = None
    notificacion.semaforo = "ROJO"
    notificacion.dias_restantes = None
    notificacion.cantidad_afectada = "10 KG"
    notificacion.leida = False
    notificacion.activa = True
    notificacion.fecha_creacion = datetime.now()
    notificacion.fecha_lectura = None
    return notificacion


# ==================== FIXTURES DE MERMAS Y CALIDAD ====================

@pytest.fixture
def mock_merma():
    """Mock de un registro de merma."""
    merma = MagicMock()
    merma.id_merma = 1
    merma.numero_registro = "MER-2025-0001"
    merma.tipo = "VENCIMIENTO"
    merma.causa = "Producto vencido"
    merma.cantidad = Decimal("5.00")
    merma.costo_unitario = Decimal("10.00")
    merma.costo_total = Decimal("50.00")
    merma.fecha_caso = datetime.now()
    merma.id_insumo = 1
    merma.id_producto = None
    merma.id_lote = None
    merma.id_user_responsable = 1
    merma.observacion = "Producto retirado por vencimiento"
    merma.estado = "REGISTRADO"
    merma.anulado = False
    return merma


# ==================== FIXTURES DE PROMOCIONES ====================

@pytest.fixture
def mock_promocion():
    """Mock de una promoción."""
    promocion = MagicMock()
    promocion.id_promocion = 1
    promocion.codigo_promocion = "PROMO001"
    promocion.titulo = "Descuento 20%"
    promocion.descripcion = "Promoción de prueba"
    promocion.tipo_promocion = MagicMock(value="DESCUENTO")
    promocion.estado = MagicMock(value="ACTIVA")
    promocion.id_producto = 1
    promocion.porcentaje_descuento = Decimal("20.00")
    promocion.precio_promocional = None
    promocion.cantidad_minima = 1
    promocion.fecha_inicio = date.today()
    promocion.fecha_fin = date.today()
    promocion.dias_hasta_vencimiento = 5
    promocion.motivo = "Promoción de prueba"
    promocion.ahorro_potencial = Decimal("100.00")
    promocion.veces_aplicada = 0
    promocion.fecha_creacion = datetime.now()
    promocion.fecha_modificacion = None
    promocion.creado_automaticamente = False
    promocion.anulado = False
    promocion.producto = None
    promocion.productos_combo = []
    return promocion


# ==================== FIXTURES DE VENTAS ====================

@pytest.fixture
def mock_venta():
    """Mock de una venta."""
    venta = MagicMock()
    venta.id_venta = 1
    venta.numero_venta = "V-2025-0001"
    venta.fecha_venta = datetime.now()
    venta.total = Decimal("100.00")
    venta.metodo_pago = "EFECTIVO"
    venta.id_user = 1
    venta.observaciones = None
    venta.anulado = False
    venta.detalles = []
    return venta


# ==================== FIXTURES DE EMPRESA ====================

@pytest.fixture
def mock_empresa():
    """Mock de una empresa."""
    empresa = MagicMock()
    empresa.id_empresa = 1
    empresa.ruc = "20123456789"
    empresa.razon_social = "Empresa Test S.A.C."
    empresa.nombre_empresa = "Empresa Test"
    empresa.direccion = "Av. Test 123"
    empresa.telefono = "999999999"
    empresa.email = "empresa@test.com"
    empresa.estado = True
    empresa.configuracion_alertas = {
        "dias_verde": 15,
        "dias_amarillo": 7,
        "dias_rojo": 3
    }
    
    def get_configuracion_alertas():
        return empresa.configuracion_alertas
    
    empresa.get_configuracion_alertas = get_configuracion_alertas
    return empresa


# ==================== FIXTURES DE MOVIMIENTOS ====================

@pytest.fixture
def mock_movimiento_producto():
    """Mock de un movimiento de producto terminado."""
    movimiento = MagicMock()
    movimiento.id_movimiento = 1
    movimiento.id_producto = 1
    movimiento.tipo_movimiento = "PRODUCCION"
    movimiento.cantidad = Decimal("10.00")
    movimiento.fecha_movimiento = datetime.now()
    movimiento.id_user = 1
    movimiento.observaciones = None
    movimiento.anulado = False
    return movimiento


# ==================== HELPERS ====================

@pytest.fixture
def fecha_hoy():
    """Retorna la fecha de hoy."""
    return date.today()


@pytest.fixture
def datetime_ahora():
    """Retorna el datetime actual."""
    return datetime.now()
