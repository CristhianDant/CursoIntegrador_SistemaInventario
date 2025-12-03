"""
Tests unitarios para MovimientoProductoTerminadoService.

Este módulo contiene tests para validar el comportamiento del servicio de
movimientos de productos terminados utilizando mocks para aislar la lógica del servicio.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from fastapi import HTTPException

from modules.gestion_almacen_productos.movimiento_productos_terminados.service import MovimientoProductoTerminadoService
from modules.gestion_almacen_productos.movimiento_productos_terminados.schemas import (
    MovimientoProductoTerminado,
    MovimientoProductoTerminadoCreate
)
from enums.tipo_movimiento import TipoMovimientoEnum


# ==================== FIXTURES ====================

@pytest.fixture
def mock_db_session():
    """Mock de la sesión de base de datos."""
    session = MagicMock()
    return session


@pytest.fixture
def mock_movimiento():
    """Mock de un movimiento de producto terminado."""
    movimiento = Mock()
    movimiento.id_movimiento = 1
    movimiento.numero_movimiento = "MOV-001"
    movimiento.id_producto = 1
    movimiento.tipo_movimiento = TipoMovimientoEnum.ENTRADA
    movimiento.motivo = "Producción"
    movimiento.cantidad = Decimal("50")
    movimiento.precio_venta = Decimal("10.00")
    movimiento.id_user = 1
    movimiento.id_documento_origen = None
    movimiento.tipo_documento_origen = None
    movimiento.observaciones = "Lote de producción diario"
    movimiento.fecha_movimiento = datetime(2025, 1, 1, 10, 0, 0)
    movimiento.anulado = False
    return movimiento


@pytest.fixture
def mock_movimiento_salida():
    """Mock de un movimiento de salida."""
    movimiento = Mock()
    movimiento.id_movimiento = 2
    movimiento.numero_movimiento = "MOV-002"
    movimiento.id_producto = 1
    movimiento.tipo_movimiento = TipoMovimientoEnum.SALIDA
    movimiento.motivo = "Venta"
    movimiento.cantidad = Decimal("10")
    movimiento.precio_venta = Decimal("10.00")
    movimiento.id_user = 1
    movimiento.id_documento_origen = 1
    movimiento.tipo_documento_origen = "VENTA"
    movimiento.observaciones = "Venta V-001"
    movimiento.fecha_movimiento = datetime(2025, 1, 1, 15, 0, 0)
    movimiento.anulado = False
    return movimiento


@pytest.fixture
def mock_movimiento_create():
    """Mock de datos para crear movimiento."""
    return MovimientoProductoTerminadoCreate(
        numero_movimiento="MOV-003",
        id_producto=1,
        tipo_movimiento=TipoMovimientoEnum.ENTRADA,
        motivo="Producción",
        cantidad=Decimal("100"),
        precio_venta=Decimal("10.00"),
        id_user=1,
        observaciones="Nuevo lote"
    )


# ==================== TEST CLASS ====================

class TestMovimientoProductoTerminadoService:
    """Tests para MovimientoProductoTerminadoService."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura el servicio antes de cada test."""
        self.service = MovimientoProductoTerminadoService()

    # -------------------- GET ALL --------------------

    def test_get_all_retorna_lista(self, mock_db_session, mock_movimiento, mock_movimiento_salida):
        """
        Test: Obtener todos los movimientos.
        
        Resultado esperado:
        - Retorna lista con todos los movimientos
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = [mock_movimiento, mock_movimiento_salida]
            
            # Act
            resultado = self.service.get_all(mock_db_session)
            
            # Assert
            assert len(resultado) == 2
            mock_get.assert_called_once_with(mock_db_session)

    def test_get_all_lista_vacia(self, mock_db_session):
        """
        Test: Obtener movimientos cuando no hay ninguno.
        
        Resultado esperado:
        - Retorna lista vacía
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = []
            
            # Act
            resultado = self.service.get_all(mock_db_session)
            
            # Assert
            assert resultado == []

    # -------------------- GET BY ID --------------------

    def test_get_by_id_existente(self, mock_db_session, mock_movimiento):
        """
        Test: Obtener movimiento por ID cuando existe.
        
        Resultado esperado:
        - Retorna el movimiento solicitado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = mock_movimiento
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, movimiento_id=1)
            
            # Assert
            assert resultado.id_movimiento == 1
            assert resultado.tipo_movimiento == TipoMovimientoEnum.ENTRADA
            mock_get.assert_called_once_with(mock_db_session, 1)

    def test_get_by_id_no_encontrado(self, mock_db_session):
        """
        Test: Obtener movimiento por ID cuando no existe.
        
        Resultado esperado:
        - Lanza HTTPException 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_by_id(mock_db_session, movimiento_id=999)
            
            assert exc_info.value.status_code == 404
            assert "no encontrado" in exc_info.value.detail

    # -------------------- CREATE --------------------

    def test_create_entrada_exitoso(self, mock_db_session, mock_movimiento_create, mock_movimiento):
        """
        Test: Crear movimiento de entrada exitosamente.
        
        Resultado esperado:
        - Retorna el movimiento creado
        """
        # Arrange
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_movimiento
            
            # Act
            resultado = self.service.create(mock_db_session, mock_movimiento_create)
            
            # Assert
            assert resultado.id_movimiento == 1
            assert resultado.tipo_movimiento == TipoMovimientoEnum.ENTRADA
            mock_create.assert_called_once_with(mock_db_session, mock_movimiento_create)

    def test_create_salida_exitoso(self, mock_db_session, mock_movimiento_salida):
        """
        Test: Crear movimiento de salida exitosamente.
        
        Resultado esperado:
        - Retorna el movimiento creado con tipo SALIDA
        """
        # Arrange
        movimiento_salida_create = MovimientoProductoTerminadoCreate(
            numero_movimiento="MOV-004",
            id_producto=1,
            tipo_movimiento=TipoMovimientoEnum.SALIDA,
            motivo="Venta",
            cantidad=Decimal("10"),
            precio_venta=Decimal("10.00"),
            id_user=1,
            id_documento_origen=1,
            tipo_documento_origen="VENTA",
            observaciones="Venta al cliente"
        )
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_movimiento_salida
            
            # Act
            resultado = self.service.create(mock_db_session, movimiento_salida_create)
            
            # Assert
            assert resultado.tipo_movimiento == TipoMovimientoEnum.SALIDA
            assert resultado.id_documento_origen == 1

    def test_create_con_documento_origen(self, mock_db_session, mock_movimiento_salida):
        """
        Test: Crear movimiento vinculado a documento de origen.
        
        Resultado esperado:
        - Movimiento tiene referencia al documento origen
        """
        # Arrange
        movimiento_con_doc = MovimientoProductoTerminadoCreate(
            numero_movimiento="MOV-005",
            id_producto=1,
            tipo_movimiento=TipoMovimientoEnum.SALIDA,
            motivo="Venta",
            cantidad=Decimal("5"),
            precio_venta=Decimal("10.00"),
            id_user=1,
            id_documento_origen=123,
            tipo_documento_origen="VENTA"
        )
        
        mock_resultado = Mock()
        mock_resultado.id_movimiento = 3
        mock_resultado.id_documento_origen = 123
        mock_resultado.tipo_documento_origen = "VENTA"
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_resultado
            
            # Act
            resultado = self.service.create(mock_db_session, movimiento_con_doc)
            
            # Assert
            assert resultado.id_documento_origen == 123
            assert resultado.tipo_documento_origen == "VENTA"
