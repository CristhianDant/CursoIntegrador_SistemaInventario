"""
Tests unitarios para ProveedorService.

Este módulo contiene tests para validar el comportamiento del servicio de proveedores
utilizando mocks para aislar la lógica del servicio de las dependencias externas.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException

from modules.proveedores.service import ProveedorService
from modules.proveedores.model import Proveedor
from modules.proveedores.schemas import ProveedorCreate, ProveedorUpdate


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
def mock_proveedor():
    """Mock de un proveedor."""
    proveedor = MagicMock(spec=Proveedor)
    proveedor.id_proveedor = 1
    proveedor.ruc_dni = "20123456789"
    proveedor.razon_social = "Proveedor Test S.A.C."
    proveedor.direccion = "Av. Proveedor 123"
    proveedor.telefono = "999999999"
    proveedor.email = "proveedor@test.com"
    proveedor.contacto = "Juan Perez"
    proveedor.anulado = False
    return proveedor


@pytest.fixture
def mock_proveedor_create():
    """Mock de datos para crear un proveedor."""
    return ProveedorCreate(
        nombre="Nuevo Proveedor S.A.C.",
        ruc_dni="20987654321",
        numero_contacto="888888888",
        email_contacto="nuevo@proveedor.com",
        direccion_fiscal="Av. Nueva 456"
    )


@pytest.fixture
def mock_proveedor_update():
    """Mock de datos para actualizar un proveedor."""
    return ProveedorUpdate(
        nombre="Proveedor Actualizado S.A.C.",
        direccion_fiscal="Av. Actualizada 789"
    )


# ==================== TEST CLASS ====================

class TestProveedorService:
    """Tests para ProveedorService."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_db_session):
        """Configura el servicio antes de cada test."""
        self.service = ProveedorService(mock_db_session)
        self.mock_db = mock_db_session

    # -------------------- GET PROVEEDORES --------------------

    def test_get_proveedores_retorna_lista(self, mock_proveedor):
        """
        Test: Obtener todos los proveedores.
        
        Resultado esperado:
        - Retorna una lista con todos los proveedores
        """
        # Arrange
        lista_proveedores = [mock_proveedor]
        with patch.object(self.service.repository, 'get_proveedores') as mock_get:
            mock_get.return_value = lista_proveedores

            # Act
            resultado = self.service.get_proveedores()

            # Assert
            assert resultado == lista_proveedores
            assert len(resultado) == 1
            mock_get.assert_called_once_with(skip=0, limit=100)

    def test_get_proveedores_con_paginacion(self, mock_proveedor):
        """
        Test: Obtener proveedores con paginación.
        
        Resultado esperado:
        - Usa los parámetros skip y limit correctamente
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedores') as mock_get:
            mock_get.return_value = [mock_proveedor]

            # Act
            resultado = self.service.get_proveedores(skip=10, limit=50)

            # Assert
            mock_get.assert_called_once_with(skip=10, limit=50)

    def test_get_proveedores_lista_vacia(self):
        """
        Test: Obtener proveedores cuando no hay ninguno.
        
        Resultado esperado:
        - Retorna una lista vacía
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedores') as mock_get:
            mock_get.return_value = []

            # Act
            resultado = self.service.get_proveedores()

            # Assert
            assert resultado == []

    # -------------------- GET PROVEEDOR --------------------

    def test_get_proveedor_existente(self, mock_proveedor):
        """
        Test: Obtener proveedor por ID cuando existe.
        
        Resultado esperado:
        - Retorna el proveedor solicitado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedor') as mock_get:
            mock_get.return_value = mock_proveedor

            # Act
            resultado = self.service.get_proveedor(proveedor_id=1)

            # Assert
            assert resultado.id_proveedor == 1
            assert resultado.ruc_dni == "20123456789"
            mock_get.assert_called_once_with(proveedor_id=1)

    def test_get_proveedor_no_existente(self):
        """
        Test: Obtener proveedor por ID cuando no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedor') as mock_get:
            mock_get.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_proveedor(proveedor_id=999)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Proveedor no encontrado"

    # -------------------- CREATE PROVEEDOR --------------------

    def test_create_proveedor_exitoso(self, mock_proveedor_create, mock_proveedor):
        """
        Test: Crear proveedor exitosamente.
        
        Resultado esperado:
        - Retorna el proveedor creado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedor_by_ruc_dni') as mock_get_ruc, \
             patch.object(self.service.repository, 'create_proveedor') as mock_create:
            mock_get_ruc.return_value = None  # RUC/DNI no existe
            mock_create.return_value = mock_proveedor

            # Act
            resultado = self.service.create_proveedor(proveedor=mock_proveedor_create)

            # Assert
            assert resultado.id_proveedor == 1
            mock_get_ruc.assert_called_once_with(ruc_dni=mock_proveedor_create.ruc_dni)
            mock_create.assert_called_once_with(proveedor=mock_proveedor_create)

    def test_create_proveedor_ruc_dni_duplicado(self, mock_proveedor_create, mock_proveedor):
        """
        Test: Crear proveedor con RUC/DNI ya existente.
        
        Resultado esperado:
        - Lanza HTTPException con status 400
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedor_by_ruc_dni') as mock_get_ruc:
            mock_get_ruc.return_value = mock_proveedor  # RUC/DNI ya existe

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.create_proveedor(proveedor=mock_proveedor_create)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "RUC/DNI ya registrado"

    # -------------------- UPDATE PROVEEDOR --------------------

    def test_update_proveedor_exitoso(self, mock_proveedor_update, mock_proveedor):
        """
        Test: Actualizar proveedor exitosamente.
        
        Resultado esperado:
        - Retorna el proveedor actualizado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedor') as mock_get, \
             patch.object(self.service.repository, 'update_proveedor') as mock_update:
            mock_get.return_value = mock_proveedor
            mock_proveedor.razon_social = "Proveedor Actualizado S.A.C."
            mock_update.return_value = mock_proveedor

            # Act
            resultado = self.service.update_proveedor(proveedor_id=1, proveedor=mock_proveedor_update)

            # Assert
            assert resultado.razon_social == "Proveedor Actualizado S.A.C."
            mock_get.assert_called_once_with(proveedor_id=1)
            mock_update.assert_called_once_with(proveedor_id=1, proveedor=mock_proveedor_update)

    def test_update_proveedor_no_existente(self, mock_proveedor_update):
        """
        Test: Actualizar proveedor que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedor') as mock_get:
            mock_get.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.update_proveedor(proveedor_id=999, proveedor=mock_proveedor_update)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Proveedor no encontrado"

    def test_update_proveedor_ruc_dni_duplicado(self, mock_proveedor):
        """
        Test: Actualizar proveedor con RUC/DNI que ya pertenece a otro proveedor.
        
        Resultado esperado:
        - Lanza HTTPException con status 400
        """
        # Arrange
        otro_proveedor = MagicMock(spec=Proveedor)
        otro_proveedor.id_proveedor = 2
        otro_proveedor.ruc_dni = "20111111111"

        update_data = ProveedorUpdate(ruc_dni="20111111111")

        with patch.object(self.service.repository, 'get_proveedor') as mock_get, \
             patch.object(self.service.repository, 'get_proveedor_by_ruc_dni') as mock_get_ruc:
            mock_get.return_value = mock_proveedor
            mock_get_ruc.return_value = otro_proveedor  # RUC/DNI pertenece a otro proveedor

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.update_proveedor(proveedor_id=1, proveedor=update_data)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "RUC/DNI ya pertenece a otro proveedor"

    # -------------------- DELETE PROVEEDOR --------------------

    def test_delete_proveedor_exitoso(self, mock_proveedor):
        """
        Test: Eliminar proveedor exitosamente.
        
        Resultado esperado:
        - Retorna el proveedor eliminado (soft delete)
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedor') as mock_get, \
             patch.object(self.service.repository, 'delete_proveedor') as mock_delete:
            mock_get.return_value = mock_proveedor
            mock_proveedor.anulado = True
            mock_delete.return_value = mock_proveedor

            # Act
            resultado = self.service.delete_proveedor(proveedor_id=1)

            # Assert
            assert resultado.anulado == True
            mock_delete.assert_called_once_with(proveedor_id=1)

    def test_delete_proveedor_no_existente(self):
        """
        Test: Eliminar proveedor que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_proveedor') as mock_get:
            mock_get.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.delete_proveedor(proveedor_id=999)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Proveedor no encontrado"
