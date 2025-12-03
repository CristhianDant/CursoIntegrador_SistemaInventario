"""
Tests unitarios para RolService.

Este módulo contiene tests para validar el comportamiento del servicio de roles
utilizando mocks para aislar la lógica del servicio.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from modules.Gestion_Usuarios.roles.service import RolService
from modules.Gestion_Usuarios.roles.model import Rol
from modules.Gestion_Usuarios.roles.schemas import RolCreate, RolUpdate


# ==================== FIXTURES ADICIONALES ====================

@pytest.fixture
def mock_rol_create():
    """Mock de datos para crear un rol."""
    return RolCreate(
        nombre_rol="Vendedor",
        descripcion="Rol para personal de ventas",
        lista_permisos=[1, 2, 3]
    )


@pytest.fixture
def mock_rol_update():
    """Mock de datos para actualizar un rol."""
    return RolUpdate(
        id_rol=1,
        nombre_rol="Vendedor Senior",
        descripcion="Vendedor con más permisos",
        lista_permisos=[1, 2, 3, 4]
    )


# ==================== TEST CLASS ====================

class TestRolService:
    """Tests para RolService."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura el servicio antes de cada test."""
        self.service = RolService()

    # -------------------- GET ALL --------------------

    def test_get_all_retorna_lista(self, mock_db_session, mock_rol):
        """
        Test: Obtener todos los roles.
        
        Resultado esperado:
        - Retorna lista con todos los roles
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = [mock_rol]
            
            # Act
            resultado = self.service.get_all(mock_db_session)
            
            # Assert
            assert len(resultado) == 1
            mock_get.assert_called_once_with(mock_db_session)

    def test_get_all_lista_vacia(self, mock_db_session):
        """
        Test: Obtener roles cuando no hay ninguno.
        
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

    def test_get_by_id_existente(self, mock_db_session, mock_rol):
        """
        Test: Obtener rol por ID cuando existe.
        
        Resultado esperado:
        - Retorna el rol solicitado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = mock_rol
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, rol_id=1)
            
            # Assert
            assert resultado.id_rol == 1
            mock_get.assert_called_once_with(mock_db_session, 1)

    def test_get_by_id_no_encontrado(self, mock_db_session):
        """
        Test: Obtener rol por ID cuando no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, rol_id=999)
            
            # Assert
            assert resultado is None

    # -------------------- CREATE --------------------

    def test_create_exitoso(self, mock_db_session, mock_rol_create, mock_rol):
        """
        Test: Crear rol exitosamente.
        
        Resultado esperado:
        - Retorna el rol creado con permisos asignados
        """
        # Arrange
        with patch.object(self.service.permiso_repository, 'get_by_id') as mock_perm, \
             patch.object(self.service.repository, 'create_rol') as mock_create, \
             patch.object(self.service.repository, 'save_permissions_rol') as mock_save_perm:
            mock_perm.return_value = MagicMock()  # Permisos existen
            mock_create.return_value = mock_rol
            
            # Act
            resultado = self.service.create(mock_db_session, mock_rol_create)
            
            # Assert
            assert resultado.id_rol == 1
            mock_db_session.commit.assert_called()
            mock_db_session.refresh.assert_called_with(mock_rol)

    def test_create_sin_permisos(self, mock_db_session, mock_rol):
        """
        Test: Crear rol sin permisos asignados.
        
        Resultado esperado:
        - Se crea correctamente sin permisos
        """
        # Arrange
        rol_sin_permisos = RolCreate(
            nombre_rol="Rol Básico",
            descripcion="Sin permisos",
            lista_permisos=[]
        )
        
        with patch.object(self.service.repository, 'create_rol') as mock_create:
            mock_create.return_value = mock_rol
            
            # Act
            resultado = self.service.create(mock_db_session, rol_sin_permisos)
            
            # Assert
            mock_create.assert_called_once()

    def test_create_permiso_no_existe(self, mock_db_session, mock_rol_create):
        """
        Test: Crear rol con permiso inexistente.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        with patch.object(self.service.permiso_repository, 'get_by_id') as mock_perm:
            mock_perm.return_value = None  # Permiso no existe
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.create(mock_db_session, mock_rol_create)
            
            assert "permiso con ID" in str(exc_info.value)

    def test_create_valida_todos_los_permisos(self, mock_db_session, mock_rol):
        """
        Test: Verificar que se validan todos los permisos antes de crear.
        
        Resultado esperado:
        - Se valida cada permiso de la lista
        """
        # Arrange
        rol_data = RolCreate(
            nombre_rol="Test",
            lista_permisos=[1, 2, 3]
        )
        
        with patch.object(self.service.permiso_repository, 'get_by_id') as mock_perm, \
             patch.object(self.service.repository, 'create_rol') as mock_create, \
             patch.object(self.service.repository, 'save_permissions_rol'):
            mock_perm.return_value = MagicMock()
            mock_create.return_value = mock_rol
            
            # Act
            self.service.create(mock_db_session, rol_data)
            
            # Assert
            assert mock_perm.call_count == 3

    # -------------------- UPDATE --------------------

    def test_update_exitoso(self, mock_db_session, mock_rol_update, mock_rol):
        """
        Test: Actualizar rol existente.
        
        Resultado esperado:
        - Retorna el rol actualizado
        """
        # Arrange
        mock_rol.nombre_rol = "Vendedor Senior"
        
        with patch.object(self.service.repository, 'get_by_id') as mock_get, \
             patch.object(self.service.permiso_repository, 'get_by_id') as mock_perm, \
             patch.object(self.service.repository, 'update') as mock_update, \
             patch.object(self.service.repository, 'clear_permissions_from_rol') as mock_clear, \
             patch.object(self.service.repository, 'save_permissions_rol') as mock_save:
            mock_get.return_value = mock_rol
            mock_perm.return_value = MagicMock()
            
            # Act
            resultado = self.service.update(mock_db_session, rol_id=1, rol_update=mock_rol_update)
            
            # Assert
            assert resultado.nombre_rol == "Vendedor Senior"
            mock_db_session.commit.assert_called()

    def test_update_rol_no_existe(self, mock_db_session, mock_rol_update):
        """
        Test: Actualizar rol que no existe.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.update(mock_db_session, rol_id=999, rol_update=mock_rol_update)
            
            assert "rol no existe" in str(exc_info.value)

    def test_update_permiso_no_existe(self, mock_db_session, mock_rol):
        """
        Test: Actualizar rol con permiso inexistente.
        
        Resultado esperado:
        - Lanza ValueError y hace rollback
        """
        # Arrange
        update_data = RolUpdate(id_rol=1, lista_permisos=[999])
        
        with patch.object(self.service.repository, 'get_by_id') as mock_get, \
             patch.object(self.service.permiso_repository, 'get_by_id') as mock_perm:
            mock_get.return_value = mock_rol
            mock_perm.return_value = None
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.update(mock_db_session, rol_id=1, rol_update=update_data)
            
            mock_db_session.rollback.assert_called()

    def test_update_limpia_permisos_anteriores(self, mock_db_session, mock_rol):
        """
        Test: Al actualizar permisos, se limpian los anteriores.
        
        Resultado esperado:
        - Se llama clear_permissions_from_rol antes de guardar nuevos
        """
        # Arrange
        update_data = RolUpdate(id_rol=1, lista_permisos=[5, 6])
        
        with patch.object(self.service.repository, 'get_by_id') as mock_get, \
             patch.object(self.service.permiso_repository, 'get_by_id') as mock_perm, \
             patch.object(self.service.repository, 'update') as mock_update, \
             patch.object(self.service.repository, 'clear_permissions_from_rol') as mock_clear, \
             patch.object(self.service.repository, 'save_permissions_rol') as mock_save:
            mock_get.return_value = mock_rol
            mock_perm.return_value = MagicMock()
            
            # Act
            self.service.update(mock_db_session, rol_id=1, rol_update=update_data)
            
            # Assert
            mock_clear.assert_called_once_with(mock_db_session, mock_rol)
            mock_save.assert_called_once()

    def test_update_sin_cambiar_permisos(self, mock_db_session, mock_rol):
        """
        Test: Actualizar rol sin cambiar permisos.
        
        Resultado esperado:
        - No se limpian ni guardan permisos
        """
        # Arrange
        update_data = RolUpdate(id_rol=1, nombre_rol="Nuevo Nombre")
        
        with patch.object(self.service.repository, 'get_by_id') as mock_get, \
             patch.object(self.service.repository, 'update') as mock_update, \
             patch.object(self.service.repository, 'clear_permissions_from_rol') as mock_clear:
            mock_get.return_value = mock_rol
            
            # Act
            self.service.update(mock_db_session, rol_id=1, rol_update=update_data)
            
            # Assert
            mock_clear.assert_not_called()

    # -------------------- DELETE --------------------

    def test_delete_exitoso(self, mock_db_session):
        """
        Test: Eliminar (anular) rol exitosamente.
        
        Resultado esperado:
        - Retorna True
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = True
            
            # Act
            resultado = self.service.delete(mock_db_session, rol_id=1)
            
            # Assert
            assert resultado is True
            mock_delete.assert_called_once_with(mock_db_session, 1)

    def test_delete_no_encontrado(self, mock_db_session):
        """
        Test: Eliminar rol que no existe.
        
        Resultado esperado:
        - Retorna False
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = False
            
            # Act
            resultado = self.service.delete(mock_db_session, rol_id=999)
            
            # Assert
            assert resultado is False
