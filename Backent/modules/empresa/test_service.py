"""
Tests unitarios para EmpresaService.

Este módulo contiene tests para validar el comportamiento del servicio de empresa
utilizando mocks para aislar la lógica del servicio de las dependencias externas.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException

from modules.empresa.service import EmpresaService
from modules.empresa.model import Empresa
from modules.empresa.schemas import EmpresaCreate, EmpresaUpdate


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
def mock_empresa():
    """Mock de una empresa."""
    empresa = MagicMock(spec=Empresa)
    empresa.id_empresa = 1
    empresa.ruc = "20123456789"
    empresa.razon_social = "Empresa Test S.A.C."
    empresa.direccion = "Av. Test 123"
    empresa.telefono = "999999999"
    empresa.email = "test@empresa.com"
    empresa.estado = True
    return empresa


@pytest.fixture
def mock_empresa_create():
    """Mock de datos para crear una empresa."""
    return EmpresaCreate(
        nombre_empresa="Nueva Empresa",
        ruc="20987654321",
        direccion="Av. Nueva 456",
        telefono="888888888",
        email="nueva@empresa.com"
    )


@pytest.fixture
def mock_empresa_update():
    """Mock de datos para actualizar una empresa."""
    return EmpresaUpdate(
        nombre_empresa="Empresa Actualizada S.A.C.",
        direccion="Av. Actualizada 789"
    )


# ==================== TEST CLASS ====================

class TestEmpresaService:
    """Tests para EmpresaService."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_db_session):
        """Configura el servicio antes de cada test."""
        self.service = EmpresaService(mock_db_session)
        self.mock_db = mock_db_session

    # -------------------- GET EMPRESAS --------------------

    def test_get_empresas_retorna_lista(self, mock_empresa):
        """
        Test: Obtener todas las empresas.
        
        Resultado esperado:
        - Retorna una lista con todas las empresas
        """
        # Arrange
        lista_empresas = [mock_empresa]
        with patch.object(self.service.repository, 'get_empresas') as mock_get:
            mock_get.return_value = lista_empresas

            # Act
            resultado = self.service.get_empresas()

            # Assert
            assert resultado == lista_empresas
            assert len(resultado) == 1
            mock_get.assert_called_once_with(skip=0, limit=100)

    def test_get_empresas_con_paginacion(self, mock_empresa):
        """
        Test: Obtener empresas con paginación.
        
        Resultado esperado:
        - Usa los parámetros skip y limit correctamente
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresas') as mock_get:
            mock_get.return_value = [mock_empresa]

            # Act
            resultado = self.service.get_empresas(skip=10, limit=50)

            # Assert
            mock_get.assert_called_once_with(skip=10, limit=50)

    def test_get_empresas_lista_vacia(self):
        """
        Test: Obtener empresas cuando no hay ninguna.
        
        Resultado esperado:
        - Retorna una lista vacía
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresas') as mock_get:
            mock_get.return_value = []

            # Act
            resultado = self.service.get_empresas()

            # Assert
            assert resultado == []

    # -------------------- GET EMPRESA --------------------

    def test_get_empresa_existente(self, mock_empresa):
        """
        Test: Obtener empresa por ID cuando existe.
        
        Resultado esperado:
        - Retorna la empresa solicitada
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresa') as mock_get:
            mock_get.return_value = mock_empresa

            # Act
            resultado = self.service.get_empresa(empresa_id=1)

            # Assert
            assert resultado.id_empresa == 1
            assert resultado.ruc == "20123456789"
            mock_get.assert_called_once_with(empresa_id=1)

    def test_get_empresa_no_existente(self):
        """
        Test: Obtener empresa por ID cuando no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresa') as mock_get:
            mock_get.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_empresa(empresa_id=999)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Empresa no encontrada"

    # -------------------- CREATE EMPRESA --------------------

    def test_create_empresa_exitoso(self, mock_empresa_create, mock_empresa):
        """
        Test: Crear empresa exitosamente.
        
        Resultado esperado:
        - Retorna la empresa creada
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresa_by_ruc') as mock_get_ruc, \
             patch.object(self.service.repository, 'create_empresa') as mock_create:
            mock_get_ruc.return_value = None  # RUC no existe
            mock_create.return_value = mock_empresa

            # Act
            resultado = self.service.create_empresa(empresa=mock_empresa_create)

            # Assert
            assert resultado.id_empresa == 1
            mock_get_ruc.assert_called_once_with(ruc=mock_empresa_create.ruc)
            mock_create.assert_called_once_with(empresa=mock_empresa_create)

    def test_create_empresa_ruc_duplicado(self, mock_empresa_create, mock_empresa):
        """
        Test: Crear empresa con RUC ya existente.
        
        Resultado esperado:
        - Lanza HTTPException con status 400
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresa_by_ruc') as mock_get_ruc:
            mock_get_ruc.return_value = mock_empresa  # RUC ya existe

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.create_empresa(empresa=mock_empresa_create)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "RUC ya registrado"

    # -------------------- UPDATE EMPRESA --------------------

    def test_update_empresa_exitoso(self, mock_empresa_update, mock_empresa):
        """
        Test: Actualizar empresa exitosamente.
        
        Resultado esperado:
        - Retorna la empresa actualizada
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresa') as mock_get, \
             patch.object(self.service.repository, 'update_empresa') as mock_update:
            mock_get.return_value = mock_empresa
            mock_empresa.razon_social = "Empresa Actualizada S.A.C."
            mock_update.return_value = mock_empresa

            # Act
            resultado = self.service.update_empresa(empresa_id=1, empresa=mock_empresa_update)

            # Assert
            assert resultado.razon_social == "Empresa Actualizada S.A.C."
            mock_get.assert_called_once_with(empresa_id=1)
            mock_update.assert_called_once_with(empresa_id=1, empresa=mock_empresa_update)

    def test_update_empresa_no_existente(self, mock_empresa_update):
        """
        Test: Actualizar empresa que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresa') as mock_get:
            mock_get.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.update_empresa(empresa_id=999, empresa=mock_empresa_update)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Empresa no encontrada"

    def test_update_empresa_ruc_duplicado(self, mock_empresa):
        """
        Test: Actualizar empresa con RUC que ya pertenece a otra empresa.
        
        Resultado esperado:
        - Lanza HTTPException con status 400
        """
        # Arrange
        otra_empresa = MagicMock(spec=Empresa)
        otra_empresa.id_empresa = 2
        otra_empresa.ruc = "20111111111"

        update_data = EmpresaUpdate(ruc="20111111111")

        with patch.object(self.service.repository, 'get_empresa') as mock_get, \
             patch.object(self.service.repository, 'get_empresa_by_ruc') as mock_get_ruc:
            mock_get.return_value = mock_empresa
            mock_get_ruc.return_value = otra_empresa  # RUC pertenece a otra empresa

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.update_empresa(empresa_id=1, empresa=update_data)

            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "RUC ya pertenece a otra empresa"

    # -------------------- DELETE EMPRESA --------------------

    def test_delete_empresa_exitoso(self, mock_empresa):
        """
        Test: Eliminar empresa exitosamente.
        
        Resultado esperado:
        - Retorna la empresa eliminada (soft delete)
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresa') as mock_get, \
             patch.object(self.service.repository, 'delete_empresa') as mock_delete:
            mock_get.return_value = mock_empresa
            mock_empresa.estado = False
            mock_delete.return_value = mock_empresa

            # Act
            resultado = self.service.delete_empresa(empresa_id=1)

            # Assert
            assert resultado.estado == False
            mock_delete.assert_called_once_with(empresa_id=1)

    def test_delete_empresa_no_existente(self):
        """
        Test: Eliminar empresa que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_empresa') as mock_get:
            mock_get.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.delete_empresa(empresa_id=999)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Empresa no encontrada"
