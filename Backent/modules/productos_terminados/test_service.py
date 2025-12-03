"""
Tests unitarios para ProductoTerminadoService.

Este módulo contiene tests para validar el comportamiento del servicio de productos terminados
utilizando mocks para aislar la lógica del servicio.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import datetime

from modules.productos_terminados.service import ProductoTerminadoService
from modules.productos_terminados.model import ProductoTerminado as ProductoTerminadoModel
from modules.productos_terminados.schemas import (
    ProductoTerminadoCreate, ProductoTerminadoUpdate, ProductoTerminado
)


# ==================== FIXTURES ADICIONALES ====================

@pytest.fixture
def mock_producto_create():
    """Mock de datos para crear un producto terminado."""
    return ProductoTerminadoCreate(
        codigo_producto="PROD002",
        nombre="Pan Integral",
        descripcion="Pan integral de trigo",
        unidad_medida="KG",
        stock_minimo=Decimal("10.00"),
        vida_util_dias=5,
        precio_venta=Decimal("3.50")
    )


@pytest.fixture
def mock_producto_update():
    """Mock de datos para actualizar un producto terminado."""
    return ProductoTerminadoUpdate(
        codigo_producto="PROD002",
        nombre="Pan Integral Premium",
        descripcion="Pan integral premium",
        unidad_medida="KG",
        stock_minimo=Decimal("15.00"),
        vida_util_dias=7,
        precio_venta=Decimal("4.50")
    )


# ==================== TEST CLASS ====================

class TestProductoTerminadoService:
    """Tests para ProductoTerminadoService."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura el servicio antes de cada test."""
        self.service = ProductoTerminadoService()

    # -------------------- GET ALL --------------------

    def test_get_all_retorna_lista(self, mock_db_session, mock_producto_terminado):
        """
        Test: Obtener todos los productos terminados.
        
        Resultado esperado:
        - Retorna lista con todos los productos
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = [mock_producto_terminado]
            
            # Act
            resultado = self.service.get_all(mock_db_session)
            
            # Assert
            assert len(resultado) == 1
            mock_get.assert_called_once_with(mock_db_session)

    def test_get_all_lista_vacia(self, mock_db_session):
        """
        Test: Obtener productos cuando no hay ninguno.
        
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

    def test_get_by_id_existente(self, mock_db_session, mock_producto_terminado):
        """
        Test: Obtener producto por ID cuando existe.
        
        Resultado esperado:
        - Retorna el producto solicitado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = mock_producto_terminado
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, producto_id=1)
            
            # Assert
            assert resultado.id_producto == 1
            mock_get.assert_called_once_with(mock_db_session, 1)

    def test_get_by_id_no_encontrado(self, mock_db_session):
        """
        Test: Obtener producto por ID cuando no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, producto_id=999)
            
            # Assert
            assert resultado is None

    # -------------------- CREATE --------------------

    def test_create_exitoso(self, mock_db_session, mock_producto_create, mock_producto_terminado):
        """
        Test: Crear producto terminado exitosamente.
        
        Resultado esperado:
        - Retorna el producto creado con nombre capitalizado
        """
        # Arrange
        mock_producto_terminado.nombre = "Pan integral"  # Capitalizado
        
        with patch.object(self.service.repository, 'get_by_code') as mock_code, \
             patch.object(self.service.repository, 'create') as mock_create:
            mock_code.return_value = None  # Código no existe
            mock_create.return_value = mock_producto_terminado
            
            # Act
            resultado = self.service.create(mock_db_session, mock_producto_create)
            
            # Assert
            assert resultado is not None
            mock_code.assert_called_once_with(mock_db_session, mock_producto_create.codigo_producto)
            mock_create.assert_called_once()

    def test_create_codigo_duplicado(self, mock_db_session, mock_producto_create, mock_producto_terminado):
        """
        Test: Crear producto con código ya existente.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_code') as mock_code:
            mock_code.return_value = mock_producto_terminado  # Código ya existe
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.create(mock_db_session, mock_producto_create)
            
            assert "ya existe" in str(exc_info.value)

    def test_create_stock_minimo_negativo(self, mock_db_session):
        """
        Test: Crear producto con stock mínimo negativo.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        producto_data = ProductoTerminadoCreate(
            codigo_producto="PROD003",
            nombre="Producto Inválido",
            unidad_medida="KG",
            stock_minimo=Decimal("-5.00")  # Negativo
        )
        
        with patch.object(self.service.repository, 'get_by_code') as mock_code:
            mock_code.return_value = None
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.create(mock_db_session, producto_data)
            
            assert "stock mínimo" in str(exc_info.value).lower()

    def test_create_capitaliza_nombre(self, mock_db_session, mock_producto_terminado):
        """
        Test: Verificar que el nombre se capitaliza al crear.
        
        Resultado esperado:
        - El nombre se guarda capitalizado
        """
        # Arrange
        producto_data = ProductoTerminadoCreate(
            codigo_producto="PROD004",
            nombre="pan integral especial",  # minúsculas
            unidad_medida="KG"
        )
        
        mock_producto_terminado.nombre = "Pan integral especial"
        
        with patch.object(self.service.repository, 'get_by_code') as mock_code, \
             patch.object(self.service.repository, 'create') as mock_create:
            mock_code.return_value = None
            mock_create.return_value = mock_producto_terminado
            
            # Act
            resultado = self.service.create(mock_db_session, producto_data)
            
            # Assert
            # Verificar que se llamó create con nombre capitalizado
            call_args = mock_create.call_args[0][1]
            assert call_args.nombre == "Pan integral especial"

    # -------------------- UPDATE --------------------

    def test_update_exitoso(self, mock_db_session, mock_producto_update, mock_producto_terminado):
        """
        Test: Actualizar producto existente.
        
        Resultado esperado:
        - Retorna el producto actualizado
        """
        # Arrange
        mock_producto_terminado.nombre = "Pan integral premium"
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_producto_terminado
            
            # Act
            resultado = self.service.update(mock_db_session, producto_id=1, producto_update=mock_producto_update)
            
            # Assert
            assert resultado is not None
            mock_update.assert_called_once()

    def test_update_no_encontrado(self, mock_db_session, mock_producto_update):
        """
        Test: Actualizar producto que no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = None
            
            # Act
            resultado = self.service.update(mock_db_session, producto_id=999, producto_update=mock_producto_update)
            
            # Assert
            assert resultado is None

    def test_update_stock_minimo_negativo(self, mock_db_session):
        """
        Test: Actualizar producto con stock mínimo negativo.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        update_data = ProductoTerminadoUpdate(
            codigo_producto="PROD001",
            nombre="Producto",
            unidad_medida="KG",
            stock_minimo=Decimal("-10.00")  # Negativo
        )
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.update(mock_db_session, producto_id=1, producto_update=update_data)
        
        assert "stock mínimo" in str(exc_info.value).lower()

    def test_update_capitaliza_nombre(self, mock_db_session, mock_producto_terminado):
        """
        Test: Verificar que el nombre se capitaliza al actualizar.
        
        Resultado esperado:
        - El nombre se actualiza capitalizado
        """
        # Arrange
        update_data = ProductoTerminadoUpdate(
            codigo_producto="PROD001",
            nombre="producto actualizado",  # minúsculas
            unidad_medida="KG"
        )
        
        mock_producto_terminado.nombre = "Producto actualizado"
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_producto_terminado
            
            # Act
            resultado = self.service.update(mock_db_session, producto_id=1, producto_update=update_data)
            
            # Assert
            call_args = mock_update.call_args[0][2]
            assert call_args.nombre == "Producto actualizado"

    def test_update_parcial_sin_nombre(self, mock_db_session, mock_producto_terminado):
        """
        Test: Actualizar producto sin cambiar el nombre.
        
        Resultado esperado:
        - Solo actualiza los campos proporcionados
        """
        # Arrange
        update_data = ProductoTerminadoUpdate(
            codigo_producto="PROD001",
            nombre="",  # Vacío (no cambiar)
            unidad_medida="KG",
            stock_minimo=Decimal("20.00")
        )
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_producto_terminado
            
            # Act
            resultado = self.service.update(mock_db_session, producto_id=1, producto_update=update_data)
            
            # Assert
            mock_update.assert_called_once()

    # -------------------- DELETE --------------------

    def test_delete_exitoso(self, mock_db_session):
        """
        Test: Eliminar (anular) producto exitosamente.
        
        Resultado esperado:
        - Retorna True
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = True
            
            # Act
            resultado = self.service.delete(mock_db_session, producto_id=1)
            
            # Assert
            assert resultado is True
            mock_delete.assert_called_once_with(mock_db_session, 1)

    def test_delete_no_encontrado(self, mock_db_session):
        """
        Test: Eliminar producto que no existe.
        
        Resultado esperado:
        - Retorna False
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = False
            
            # Act
            resultado = self.service.delete(mock_db_session, producto_id=999)
            
            # Assert
            assert resultado is False

    # -------------------- CASOS DE BORDE --------------------

    def test_create_stock_minimo_cero(self, mock_db_session, mock_producto_terminado):
        """
        Test: Crear producto con stock mínimo cero.
        
        Resultado esperado:
        - Se crea correctamente
        """
        # Arrange
        producto_data = ProductoTerminadoCreate(
            codigo_producto="PROD005",
            nombre="Producto Sin Mínimo",
            unidad_medida="KG",
            stock_minimo=Decimal("0")
        )
        
        with patch.object(self.service.repository, 'get_by_code') as mock_code, \
             patch.object(self.service.repository, 'create') as mock_create:
            mock_code.return_value = None
            mock_create.return_value = mock_producto_terminado
            
            # Act
            resultado = self.service.create(mock_db_session, producto_data)
            
            # Assert
            mock_create.assert_called_once()

    def test_create_sin_vida_util(self, mock_db_session, mock_producto_terminado):
        """
        Test: Crear producto sin vida útil definida.
        
        Resultado esperado:
        - Se crea correctamente con vida_util_dias = None
        """
        # Arrange
        producto_data = ProductoTerminadoCreate(
            codigo_producto="PROD006",
            nombre="Producto Sin Vida Util",
            unidad_medida="UNIDAD",
            vida_util_dias=None
        )
        
        with patch.object(self.service.repository, 'get_by_code') as mock_code, \
             patch.object(self.service.repository, 'create') as mock_create:
            mock_code.return_value = None
            mock_create.return_value = mock_producto_terminado
            
            # Act
            resultado = self.service.create(mock_db_session, producto_data)
            
            # Assert
            mock_create.assert_called_once()

    def test_update_stock_minimo_none_no_valida(self, mock_db_session, mock_producto_terminado):
        """
        Test: Actualizar producto sin especificar stock_minimo.
        
        Resultado esperado:
        - No lanza error por validación de stock_minimo
        """
        # Arrange
        update_data = ProductoTerminadoUpdate(
            codigo_producto="PROD001",
            nombre="Producto",
            unidad_medida="KG",
            stock_minimo=None  # No especificado
        )
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_producto_terminado
            
            # Act
            resultado = self.service.update(mock_db_session, producto_id=1, producto_update=update_data)
            
            # Assert
            assert resultado is not None
