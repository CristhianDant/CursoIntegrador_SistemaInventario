"""
Tests unitarios para VentasService.

Este módulo contiene tests para validar el comportamiento del servicio de ventas
utilizando mocks para aislar la lógica del servicio.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import date, datetime, timedelta

from fastapi import HTTPException

from modules.gestion_almacen_productos.ventas.service import VentasService
from modules.gestion_almacen_productos.ventas.schemas import (
    RegistrarVentaRequest,
    VentaItemRequest,
    VentaResponse,
    VentaResumenResponse
)


# ==================== FIXTURES ====================

@pytest.fixture
def mock_db_session():
    """Mock de la sesión de base de datos."""
    session = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    return session


@pytest.fixture
def mock_item_request():
    """Mock de un item de venta."""
    return VentaItemRequest(
        id_producto=1,
        cantidad=Decimal("5"),
        precio_unitario=Decimal("10.00"),
        descuento_porcentaje=Decimal("0")
    )


@pytest.fixture
def mock_item_con_descuento():
    """Mock de un item de venta con descuento."""
    return VentaItemRequest(
        id_producto=1,
        cantidad=Decimal("5"),
        precio_unitario=Decimal("10.00"),
        descuento_porcentaje=Decimal("30")
    )


@pytest.fixture
def mock_venta_request(mock_item_request):
    """Mock de request para registrar venta."""
    return RegistrarVentaRequest(
        items=[mock_item_request],
        metodo_pago="efectivo",
        observaciones="Venta de prueba"
    )


@pytest.fixture
def mock_producto_info():
    """Mock de información de producto."""
    return {
        "id_producto": 1,
        "codigo_producto": "PROD001",
        "nombre": "Pan de Chocolate",
        "descripcion": "Delicioso pan",
        "stock_actual": Decimal("100"),
        "precio_venta": Decimal("10.00")
    }


@pytest.fixture
def mock_venta_data():
    """Mock de datos de venta creada."""
    return {
        "id_venta": 1,
        "numero_venta": "V-20250101-001",
        "fecha_venta": datetime(2025, 1, 1, 10, 0, 0),
        "total": Decimal("50.00"),
        "metodo_pago": "efectivo",
        "id_user": 1,
        "nombre_usuario": "Admin",
        "observaciones": "Venta de prueba",
        "anulado": False,
        "detalles": [
            {
                "id_detalle": 1,
                "id_producto": 1,
                "nombre_producto": "Pan de Chocolate",
                "cantidad": Decimal("5"),
                "precio_unitario": Decimal("10.00"),
                "descuento_porcentaje": Decimal("0"),
                "subtotal": Decimal("50.00")
            }
        ]
    }


@pytest.fixture
def mock_productos_disponibles():
    """Mock de lista de productos disponibles."""
    return [
        {
            "id_producto": 1,
            "codigo_producto": "PROD001",
            "nombre": "Pan de Chocolate",
            "descripcion": "Delicioso",
            "stock_actual": Decimal("100"),
            "precio_venta": Decimal("10.00")
        },
        {
            "id_producto": 2,
            "codigo_producto": "PROD002",
            "nombre": "Croissant",
            "descripcion": "Crujiente",
            "stock_actual": Decimal("50"),
            "precio_venta": Decimal("8.00")
        }
    ]


# ==================== TEST CLASS ====================

class TestVentasService:
    """Tests para VentasService."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura el servicio antes de cada test."""
        self.service = VentasService()

    # -------------------- REGISTRAR VENTA --------------------

    def test_registrar_venta_exitoso(
        self, 
        mock_db_session, 
        mock_venta_request, 
        mock_producto_info
    ):
        """
        Test: Registrar venta exitosamente.
        
        Resultado esperado:
        - Retorna VentaResponse con datos correctos
        - Se descuenta stock
        - Se crea movimiento de salida
        """
        # Arrange
        with patch.object(self.service.repository, 'get_producto_info') as mock_get_producto, \
             patch.object(self.service.repository, 'get_stock_producto') as mock_get_stock, \
             patch.object(self.service.repository, 'generar_numero_venta') as mock_generar_num, \
             patch.object(self.service.repository, 'crear_venta') as mock_crear_venta, \
             patch.object(self.service.repository, 'crear_detalle_venta') as mock_crear_detalle, \
             patch.object(self.service.repository, 'descontar_stock_producto') as mock_descontar, \
             patch.object(self.service.repository, 'crear_movimiento_salida') as mock_mov:
            
            mock_get_producto.return_value = mock_producto_info
            mock_get_stock.return_value = Decimal("100")
            mock_generar_num.return_value = "V-20250101-001"
            mock_crear_venta.return_value = {
                "id_venta": 1,
                "fecha_venta": datetime(2025, 1, 1, 10, 0, 0)
            }
            mock_crear_detalle.return_value = 1
            mock_descontar.return_value = Decimal("95")
            
            # Act
            resultado = self.service.registrar_venta(
                mock_db_session,
                mock_venta_request,
                id_user=1
            )
            
            # Assert
            assert resultado.id_venta == 1
            assert resultado.numero_venta == "V-20250101-001"
            assert resultado.total == Decimal("50.00")  # 5 * 10.00
            assert len(resultado.detalles) == 1
            mock_db_session.commit.assert_called_once()

    def test_registrar_venta_producto_no_encontrado(self, mock_db_session, mock_venta_request):
        """
        Test: Error al registrar venta con producto inexistente.
        
        Resultado esperado:
        - Lanza HTTPException 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_producto_info') as mock_get:
            mock_get.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.registrar_venta(mock_db_session, mock_venta_request, id_user=1)
            
            assert exc_info.value.status_code == 404
            assert "no encontrado" in exc_info.value.detail

    def test_registrar_venta_stock_insuficiente(
        self, 
        mock_db_session, 
        mock_venta_request,
        mock_producto_info
    ):
        """
        Test: Error al registrar venta con stock insuficiente.
        
        Resultado esperado:
        - Lanza HTTPException 400
        - Mensaje indica stock disponible y solicitado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_producto_info') as mock_get_producto, \
             patch.object(self.service.repository, 'get_stock_producto') as mock_get_stock:
            
            mock_get_producto.return_value = mock_producto_info
            mock_get_stock.return_value = Decimal("2")  # Solo hay 2, se piden 5
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.registrar_venta(mock_db_session, mock_venta_request, id_user=1)
            
            assert exc_info.value.status_code == 400
            assert "Stock insuficiente" in exc_info.value.detail
            assert "Disponible: 2" in exc_info.value.detail

    def test_registrar_venta_con_descuento_calcula_total_correcto(
        self, 
        mock_db_session, 
        mock_item_con_descuento,
        mock_producto_info
    ):
        """
        Test: Calcular total correctamente con descuento.
        
        Resultado esperado:
        - Total = cantidad * (precio - descuento)
        - 5 * (10 - 3) = 35.00 (30% descuento)
        """
        # Arrange
        request = RegistrarVentaRequest(
            items=[mock_item_con_descuento],
            metodo_pago="efectivo"
        )
        
        with patch.object(self.service.repository, 'get_producto_info') as mock_get_producto, \
             patch.object(self.service.repository, 'get_stock_producto') as mock_get_stock, \
             patch.object(self.service.repository, 'generar_numero_venta') as mock_generar_num, \
             patch.object(self.service.repository, 'crear_venta') as mock_crear_venta, \
             patch.object(self.service.repository, 'crear_detalle_venta') as mock_crear_detalle, \
             patch.object(self.service.repository, 'descontar_stock_producto') as mock_descontar, \
             patch.object(self.service.repository, 'crear_movimiento_salida') as mock_mov:
            
            mock_get_producto.return_value = mock_producto_info
            mock_get_stock.return_value = Decimal("100")
            mock_generar_num.return_value = "V-20250101-001"
            mock_crear_venta.return_value = {
                "id_venta": 1,
                "fecha_venta": datetime(2025, 1, 1, 10, 0, 0)
            }
            mock_crear_detalle.return_value = 1
            mock_descontar.return_value = Decimal("95")
            
            # Act
            resultado = self.service.registrar_venta(mock_db_session, request, id_user=1)
            
            # Assert
            # 5 * (10.00 - 30%) = 5 * 7.00 = 35.00
            assert resultado.total == Decimal("35.00")

    def test_registrar_venta_rollback_en_error(self, mock_db_session, mock_venta_request):
        """
        Test: Rollback cuando hay error inesperado.
        
        Resultado esperado:
        - Se llama rollback
        - Se propaga HTTPException 500
        """
        # Arrange
        with patch.object(self.service.repository, 'get_producto_info') as mock_get:
            mock_get.side_effect = Exception("Error de conexión")
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.registrar_venta(mock_db_session, mock_venta_request, id_user=1)
            
            assert exc_info.value.status_code == 500
            mock_db_session.rollback.assert_called()

    # -------------------- GET VENTA POR ID --------------------

    def test_get_venta_por_id_existente(self, mock_db_session, mock_venta_data):
        """
        Test: Obtener venta existente por ID.
        
        Resultado esperado:
        - Retorna VentaResponse completo con detalles
        """
        # Arrange
        with patch.object(self.service.repository, 'get_venta_por_id') as mock_get:
            mock_get.return_value = mock_venta_data
            
            # Act
            resultado = self.service.get_venta_por_id(mock_db_session, id_venta=1)
            
            # Assert
            assert resultado.id_venta == 1
            assert resultado.numero_venta == "V-20250101-001"
            assert len(resultado.detalles) == 1

    def test_get_venta_por_id_no_encontrada(self, mock_db_session):
        """
        Test: Venta no encontrada.
        
        Resultado esperado:
        - Lanza HTTPException 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_venta_por_id') as mock_get:
            mock_get.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_venta_por_id(mock_db_session, id_venta=999)
            
            assert exc_info.value.status_code == 404

    # -------------------- GET VENTAS DEL DÍA --------------------

    def test_get_ventas_del_dia(self, mock_db_session):
        """
        Test: Obtener ventas del día.
        
        Resultado esperado:
        - Retorna resumen con total de ventas y monto
        """
        # Arrange
        ventas_dia = [
            {
                "id_venta": 1,
                "numero_venta": "V-001",
                "fecha_venta": datetime(2025, 1, 1, 10, 0),
                "total": Decimal("50.00"),
                "metodo_pago": "efectivo",
                "nombre_usuario": "Admin",
                "cantidad_items": 2,
                "anulado": False
            },
            {
                "id_venta": 2,
                "numero_venta": "V-002",
                "fecha_venta": datetime(2025, 1, 1, 15, 0),
                "total": Decimal("30.00"),
                "metodo_pago": "tarjeta",
                "nombre_usuario": "Admin",
                "cantidad_items": 1,
                "anulado": False
            }
        ]
        
        with patch.object(self.service.repository, 'get_ventas_del_dia') as mock_get:
            mock_get.return_value = ventas_dia
            
            # Act
            resultado = self.service.get_ventas_del_dia(mock_db_session, fecha=date(2025, 1, 1))
            
            # Assert
            assert resultado.total_ventas == 2
            assert resultado.monto_total == Decimal("80.00")

    def test_get_ventas_del_dia_excluye_anuladas_en_monto(self, mock_db_session):
        """
        Test: Monto total excluye ventas anuladas.
        
        Resultado esperado:
        - total_ventas incluye todas
        - monto_total solo ventas no anuladas
        """
        # Arrange
        ventas_dia = [
            {
                "id_venta": 1,
                "numero_venta": "V-001",
                "fecha_venta": datetime(2025, 1, 1, 10, 0),
                "total": Decimal("50.00"),
                "metodo_pago": "efectivo",
                "nombre_usuario": "Admin",
                "cantidad_items": 2,
                "anulado": False
            },
            {
                "id_venta": 2,
                "numero_venta": "V-002",
                "fecha_venta": datetime(2025, 1, 1, 15, 0),
                "total": Decimal("30.00"),
                "metodo_pago": "tarjeta",
                "nombre_usuario": "Admin",
                "cantidad_items": 1,
                "anulado": True  # Anulada
            }
        ]
        
        with patch.object(self.service.repository, 'get_ventas_del_dia') as mock_get:
            mock_get.return_value = ventas_dia
            
            # Act
            resultado = self.service.get_ventas_del_dia(mock_db_session, fecha=date(2025, 1, 1))
            
            # Assert
            assert resultado.total_ventas == 2
            assert resultado.monto_total == Decimal("50.00")  # Solo la no anulada

    # -------------------- PRODUCTOS DISPONIBLES --------------------

    def test_get_productos_disponibles(self, mock_db_session, mock_productos_disponibles):
        """
        Test: Obtener productos disponibles para venta.
        
        Resultado esperado:
        - Retorna lista de productos con stock
        """
        # Arrange
        with patch.object(self.service.repository, 'get_productos_disponibles') as mock_get, \
             patch.object(self.service.repository, 'get_ultima_produccion_producto') as mock_prod:
            
            mock_get.return_value = mock_productos_disponibles
            mock_prod.return_value = None  # Sin producción registrada
            
            # Act
            resultado = self.service.get_productos_disponibles(mock_db_session)
            
            # Assert
            assert len(resultado) == 2
            assert resultado[0].nombre == "Pan de Chocolate"

    def test_descuento_sugerido_segun_antiguedad(self, mock_db_session, mock_productos_disponibles):
        """
        Test: Calcular descuento sugerido según días desde producción (FC-09).
        
        Resultado esperado:
        - 1 día: 30%
        - 2 días: 50%
        - 3+ días: 70%
        """
        # Arrange
        hoy = date.today()
        
        with patch.object(self.service.repository, 'get_productos_disponibles') as mock_get, \
             patch.object(self.service.repository, 'get_ultima_produccion_producto') as mock_prod:
            
            # Solo un producto para simplificar
            mock_get.return_value = [mock_productos_disponibles[0]]
            
            # Producido ayer (1 día de antigüedad)
            mock_prod.return_value = {
                "fecha_produccion": datetime.combine(hoy, datetime.min.time()) - timedelta(days=1)
            }
            
            # Act
            resultado = self.service.get_productos_disponibles(mock_db_session)
            
            # Assert
            assert resultado[0].descuento_sugerido == Decimal("30")  # 30% por 1 día

    # -------------------- ANULAR VENTA --------------------

    def test_anular_venta_exitoso(self, mock_db_session, mock_venta_data):
        """
        Test: Anular venta exitosamente.
        
        Resultado esperado:
        - Restaura stock
        - Marca venta como anulada
        """
        # Arrange
        venta_anulada = mock_venta_data.copy()
        venta_anulada["anulado"] = True
        
        with patch.object(self.service.repository, 'get_venta_por_id') as mock_get, \
             patch.object(self.service.repository, 'get_stock_producto') as mock_stock, \
             patch.object(self.service.repository, 'incrementar_stock_producto') as mock_incr, \
             patch.object(self.service.repository, 'crear_movimiento_entrada_compensacion') as mock_mov, \
             patch.object(self.service.repository, 'anular_venta') as mock_anular:
            
            mock_get.side_effect = [mock_venta_data, venta_anulada]
            mock_stock.return_value = Decimal("95")
            mock_incr.return_value = Decimal("100")
            
            # Act
            resultado = self.service.anular_venta(mock_db_session, id_venta=1, id_user=1)
            
            # Assert
            assert resultado.anulado == True
            mock_incr.assert_called_once()
            mock_anular.assert_called_once_with(mock_db_session, 1)
            mock_db_session.commit.assert_called()

    def test_anular_venta_no_encontrada(self, mock_db_session):
        """
        Test: Error al anular venta inexistente.
        
        Resultado esperado:
        - Lanza HTTPException 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_venta_por_id') as mock_get:
            mock_get.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.anular_venta(mock_db_session, id_venta=999, id_user=1)
            
            assert exc_info.value.status_code == 404

    def test_anular_venta_ya_anulada(self, mock_db_session, mock_venta_data):
        """
        Test: Error al anular venta ya anulada.
        
        Resultado esperado:
        - Lanza HTTPException 400
        """
        # Arrange
        mock_venta_data["anulado"] = True
        
        with patch.object(self.service.repository, 'get_venta_por_id') as mock_get:
            mock_get.return_value = mock_venta_data
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.anular_venta(mock_db_session, id_venta=1, id_user=1)
            
            assert exc_info.value.status_code == 400
            assert "ya está anulada" in exc_info.value.detail
