"""
Tests unitarios para InsumoService.

Este módulo contiene tests para validar el comportamiento del servicio de insumos
utilizando mocks para aislar la lógica del servicio de las dependencias externas.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal

from modules.insumo.service import InsumoService
from modules.insumo.model import Insumo as InsumoModel
from modules.insumo.schemas import Insumo, InsumoCreate, InsumoUpdate
from enums.unidad_medida import UnidadMedidaEnum
from enums.categoria_insumo import CategoriaInsumoEnum


# ==================== FIXTURES ====================

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
def mock_insumo_model():
    """Mock de un insumo (modelo de BD)."""
    insumo = MagicMock(spec=InsumoModel)
    insumo.id_insumo = 1
    insumo.codigo = "INS-001"
    insumo.nombre = "Harina"
    insumo.descripcion = "Harina de trigo"
    insumo.unidad_medida = UnidadMedidaEnum.KG.value
    insumo.categoria = CategoriaInsumoEnum.Harinas.value
    insumo.stock_minimo = Decimal("10.00")
    insumo.perecible = True
    insumo.anulado = False
    return insumo


@pytest.fixture
def mock_insumo_create():
    """Mock de datos para crear un insumo."""
    return InsumoCreate(
        codigo="INS-002",
        nombre="azucar",  # En minúsculas para probar capitalización
        descripcion="Azúcar blanca",
        unidad_medida=UnidadMedidaEnum.KG,
        categoria=CategoriaInsumoEnum.Azucares,
        stock_minimo=Decimal("5.00"),
        perecible=False
    )


@pytest.fixture
def mock_insumo_update():
    """Mock de datos para actualizar un insumo."""
    return InsumoUpdate(
        nombre="harina integral",  # En minúsculas para probar capitalización
        stock_minimo=Decimal("15.00")
    )


# ==================== TEST CLASS ====================

class TestInsumoService:
    """Tests para InsumoService."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_db_session):
        """Configura el servicio antes de cada test."""
        self.service = InsumoService(mock_db_session)
        self.mock_db = mock_db_session

    # -------------------- GET INSUMOS --------------------

    def test_get_insumos_retorna_lista(self, mock_insumo_model):
        """
        Test: Obtener todos los insumos.
        
        Resultado esperado:
        - Retorna una lista de schemas Insumo
        """
        # Arrange
        with patch.object(self.service.repository, 'get_insumos') as mock_get:
            mock_get.return_value = [mock_insumo_model]

            # Act
            resultado = self.service.get_insumos()

            # Assert
            assert len(resultado) == 1
            assert isinstance(resultado[0], Insumo)
            mock_get.assert_called_once_with(0, 100)

    def test_get_insumos_con_paginacion(self, mock_insumo_model):
        """
        Test: Obtener insumos con paginación.
        
        Resultado esperado:
        - Usa los parámetros skip y limit correctamente
        """
        # Arrange
        with patch.object(self.service.repository, 'get_insumos') as mock_get:
            mock_get.return_value = [mock_insumo_model]

            # Act
            resultado = self.service.get_insumos(skip=10, limit=50)

            # Assert
            mock_get.assert_called_once_with(10, 50)

    def test_get_insumos_lista_vacia(self):
        """
        Test: Obtener insumos cuando no hay ninguno.
        
        Resultado esperado:
        - Retorna una lista vacía
        """
        # Arrange
        with patch.object(self.service.repository, 'get_insumos') as mock_get:
            mock_get.return_value = []

            # Act
            resultado = self.service.get_insumos()

            # Assert
            assert resultado == []

    # -------------------- GET INSUMO --------------------

    def test_get_insumo_existente(self, mock_insumo_model):
        """
        Test: Obtener insumo por ID cuando existe.
        
        Resultado esperado:
        - Retorna el schema Insumo
        """
        # Arrange
        with patch.object(self.service.repository, 'get_insumo') as mock_get:
            mock_get.return_value = mock_insumo_model

            # Act
            resultado = self.service.get_insumo(insumo_id=1)

            # Assert
            assert resultado is not None
            assert isinstance(resultado, Insumo)
            mock_get.assert_called_once_with(1)

    def test_get_insumo_no_existente(self):
        """
        Test: Obtener insumo por ID cuando no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'get_insumo') as mock_get:
            mock_get.return_value = None

            # Act
            resultado = self.service.get_insumo(insumo_id=999)

            # Assert
            assert resultado is None

    # -------------------- CREATE INSUMO --------------------

    def test_create_insumo_exitoso(self, mock_insumo_create, mock_insumo_model):
        """
        Test: Crear insumo exitosamente.
        
        Resultado esperado:
        - Retorna el insumo creado
        - El nombre se capitaliza
        """
        # Arrange
        with patch.object(self.service.repository, 'get_inusmo_cod') as mock_get_cod, \
             patch.object(self.service.repository, 'create_insumo') as mock_create:
            mock_get_cod.return_value = None  # Código no existe
            mock_create.return_value = mock_insumo_model

            # Act
            resultado = self.service.create_insumo(insumo=mock_insumo_create)

            # Assert
            assert resultado is not None
            assert isinstance(resultado, Insumo)
            mock_get_cod.assert_called_once_with(mock_insumo_create.codigo)

    def test_create_insumo_codigo_duplicado(self, mock_insumo_create, mock_insumo_model):
        """
        Test: Crear insumo con código ya existente.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        with patch.object(self.service.repository, 'get_inusmo_cod') as mock_get_cod:
            mock_get_cod.return_value = mock_insumo_model  # Código ya existe

            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.create_insumo(insumo=mock_insumo_create)

            assert f"El código de insumo '{mock_insumo_create.codigo}' ya existe" in str(exc_info.value)

    def test_create_insumo_stock_minimo_negativo(self):
        """
        Test: Crear insumo con stock_minimo negativo.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        insumo_invalido = InsumoCreate(
            codigo="INS-003",
            nombre="Sal",
            unidad_medida=UnidadMedidaEnum.KG,
            categoria=CategoriaInsumoEnum.Condimentos,
            stock_minimo=Decimal("-5.00")  # Negativo
        )

        with patch.object(self.service.repository, 'get_inusmo_cod') as mock_get_cod:
            mock_get_cod.return_value = None

            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.create_insumo(insumo=insumo_invalido)

            assert "El stock mínimo debe ser mayor o igual a 0" in str(exc_info.value)

    def test_create_insumo_capitaliza_nombre(self, mock_insumo_model):
        """
        Test: Verificar que el nombre se capitaliza al crear.
        
        Resultado esperado:
        - El nombre "azucar" se convierte a "Azucar"
        """
        # Arrange
        insumo_create = InsumoCreate(
            codigo="INS-004",
            nombre="azucar refinada",
            unidad_medida=UnidadMedidaEnum.KG,
            categoria=CategoriaInsumoEnum.Azucares,
            stock_minimo=Decimal("5.00")
        )

        with patch.object(self.service.repository, 'get_inusmo_cod') as mock_get_cod, \
             patch.object(self.service.repository, 'create_insumo') as mock_create:
            mock_get_cod.return_value = None
            mock_create.return_value = mock_insumo_model

            # Act
            self.service.create_insumo(insumo=insumo_create)

            # Assert - Verificar que se llamó con el nombre capitalizado
            call_args = mock_create.call_args[0][0]
            assert call_args.nombre == "Azucar refinada"

    # -------------------- UPDATE INSUMO --------------------

    def test_update_insumo_exitoso(self, mock_insumo_update, mock_insumo_model):
        """
        Test: Actualizar insumo exitosamente.
        
        Resultado esperado:
        - Retorna el insumo actualizado
        """
        # Arrange
        with patch.object(self.service.repository, 'update_insumo') as mock_update:
            mock_update.return_value = mock_insumo_model

            # Act
            resultado = self.service.update_insumo(insumo_id=1, insumo=mock_insumo_update)

            # Assert
            assert resultado is not None
            assert isinstance(resultado, Insumo)

    def test_update_insumo_no_existente(self, mock_insumo_update):
        """
        Test: Actualizar insumo que no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'update_insumo') as mock_update:
            mock_update.return_value = None

            # Act
            resultado = self.service.update_insumo(insumo_id=999, insumo=mock_insumo_update)

            # Assert
            assert resultado is None

    def test_update_insumo_stock_minimo_negativo(self):
        """
        Test: Actualizar insumo con stock_minimo negativo.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        update_invalido = InsumoUpdate(stock_minimo=Decimal("-10.00"))

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.update_insumo(insumo_id=1, insumo=update_invalido)

        assert "El stock mínimo debe ser mayor o igual a 0" in str(exc_info.value)

    def test_update_insumo_capitaliza_nombre(self, mock_insumo_model):
        """
        Test: Verificar que el nombre se capitaliza al actualizar.
        
        Resultado esperado:
        - El nombre se capitaliza correctamente
        """
        # Arrange
        update_data = InsumoUpdate(nombre="harina integral")

        with patch.object(self.service.repository, 'update_insumo') as mock_update:
            mock_update.return_value = mock_insumo_model

            # Act
            self.service.update_insumo(insumo_id=1, insumo=update_data)

            # Assert - Verificar que se llamó con el nombre capitalizado
            call_args = mock_update.call_args[0]
            assert call_args[1].nombre == "Harina integral"

    # -------------------- DELETE INSUMO --------------------

    def test_delete_insumo_exitoso(self, mock_insumo_model):
        """
        Test: Eliminar insumo exitosamente.
        
        Resultado esperado:
        - Retorna el insumo eliminado (soft delete)
        """
        # Arrange
        with patch.object(self.service.repository, 'delete_insumo') as mock_delete:
            mock_insumo_model.anulado = True
            mock_delete.return_value = mock_insumo_model

            # Act
            resultado = self.service.delete_insumo(insumo_id=1)

            # Assert
            assert resultado is not None
            mock_delete.assert_called_once_with(1)

    def test_delete_insumo_no_existente(self):
        """
        Test: Eliminar insumo que no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'delete_insumo') as mock_delete:
            mock_delete.return_value = None

            # Act
            resultado = self.service.delete_insumo(insumo_id=999)

            # Assert
            assert resultado is None

    # -------------------- GET ULTIMOS PRECIOS --------------------

    def test_get_ultimos_precios(self):
        """
        Test: Obtener últimos precios de compra.
        
        Resultado esperado:
        - Retorna diccionario con id_insumo: precio
        """
        # Arrange
        precios_esperados = {1: 10.50, 2: 25.00, 3: 5.75}
        
        with patch.object(self.service.repository, 'get_ultimos_precios') as mock_precios:
            mock_precios.return_value = precios_esperados

            # Act
            resultado = self.service.get_ultimos_precios()

            # Assert
            assert resultado == precios_esperados
            assert resultado[1] == 10.50
            mock_precios.assert_called_once()

    def test_get_ultimos_precios_vacio(self):
        """
        Test: Obtener últimos precios cuando no hay ingresos.
        
        Resultado esperado:
        - Retorna diccionario vacío
        """
        # Arrange
        with patch.object(self.service.repository, 'get_ultimos_precios') as mock_precios:
            mock_precios.return_value = {}

            # Act
            resultado = self.service.get_ultimos_precios()

            # Assert
            assert resultado == {}
