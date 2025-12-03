"""
Tests unitarios para PermisoService.

Este módulo contiene tests para validar el comportamiento del servicio de permisos
utilizando mocks para aislar la lógica del servicio.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from modules.Gestion_Usuarios.permisos.service import PermisoService
from modules.Gestion_Usuarios.permisos.model import Permiso
from modules.Gestion_Usuarios.permisos.schemas import PermisoCreate, PermisoUpdate
from enums.tipo_modulo import TipoModulo


# ==================== FIXTURES ADICIONALES ====================

@pytest.fixture
def mock_permiso_create():
    """Mock de datos para crear un permiso."""
    return PermisoCreate(
        modulo=TipoModulo.USUARIOS,
        accion="CREATE"
    )


@pytest.fixture
def mock_permiso_update():
    """Mock de datos para actualizar un permiso."""
    return PermisoUpdate(
        modulo=TipoModulo.USUARIOS,
        accion="UPDATE"
    )


# ==================== TEST CLASS ====================

class TestPermisoService:
    """Tests para PermisoService."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura el servicio antes de cada test."""
        self.service = PermisoService()

    # -------------------- GET ALL --------------------

    def test_get_all_retorna_lista(self, mock_db_session, mock_permiso):
        """
        Test: Obtener todos los permisos.
        
        Resultado esperado:
        - Retorna lista con todos los permisos
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = [mock_permiso]
            
            # Act
            resultado = self.service.get_all(mock_db_session)
            
            # Assert
            assert len(resultado) == 1
            mock_get.assert_called_once_with(mock_db_session)

    def test_get_all_lista_vacia(self, mock_db_session):
        """
        Test: Obtener permisos cuando no hay ninguno.
        
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

    def test_get_by_id_existente(self, mock_db_session, mock_permiso):
        """
        Test: Obtener permiso por ID cuando existe.
        
        Resultado esperado:
        - Retorna el permiso solicitado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = mock_permiso
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, permiso_id=1)
            
            # Assert
            assert resultado.id_permiso == 1
            mock_get.assert_called_once_with(mock_db_session, 1)

    def test_get_by_id_no_encontrado(self, mock_db_session):
        """
        Test: Obtener permiso por ID cuando no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, permiso_id=999)
            
            # Assert
            assert resultado is None

    # -------------------- CREATE --------------------

    def test_create_exitoso(self, mock_db_session, mock_permiso_create, mock_permiso):
        """
        Test: Crear permiso exitosamente.
        
        Resultado esperado:
        - Retorna el permiso creado
        """
        # Arrange
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_permiso
            
            # Act
            resultado = self.service.create(mock_db_session, mock_permiso_create)
            
            # Assert
            assert resultado.id_permiso == 1
            mock_create.assert_called_once_with(mock_db_session, mock_permiso_create)

    # -------------------- UPDATE --------------------

    def test_update_exitoso(self, mock_db_session, mock_permiso_update, mock_permiso):
        """
        Test: Actualizar permiso existente.
        
        Resultado esperado:
        - Retorna el permiso actualizado
        """
        # Arrange
        mock_permiso.descripcion = "Descripción actualizada"
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_permiso
            
            # Act
            resultado = self.service.update(mock_db_session, permiso_id=1, permiso_update=mock_permiso_update)
            
            # Assert
            assert resultado.descripcion == "Descripción actualizada"
            mock_update.assert_called_once_with(mock_db_session, 1, mock_permiso_update)

    def test_update_no_encontrado(self, mock_db_session, mock_permiso_update):
        """
        Test: Actualizar permiso que no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = None
            
            # Act
            resultado = self.service.update(mock_db_session, permiso_id=999, permiso_update=mock_permiso_update)
            
            # Assert
            assert resultado is None
