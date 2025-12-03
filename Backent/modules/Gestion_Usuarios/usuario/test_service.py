"""
Tests unitarios para UsuarioService.

Este módulo contiene tests para validar el comportamiento del servicio de usuarios
utilizando mocks para aislar la lógica del servicio.

NO se evalúan: envío de emails de credenciales.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from modules.Gestion_Usuarios.usuario.service import UsuarioService
from modules.Gestion_Usuarios.usuario.model import Usuario
from modules.Gestion_Usuarios.usuario.schemas import UsuarioCreate, UsuarioUpdate
from modules.Gestion_Usuarios.personal.schemas import PersonalCreate, PersonalUpdate


# ==================== FIXTURES ADICIONALES ====================

@pytest.fixture
def mock_personal_create():
    """Mock de datos para crear personal."""
    return PersonalCreate(
        nombre_completo="Juan Perez Garcia",
        direccion="Calle Test 123",
        referencia="Cerca al parque",
        dni="12345678",
        area="ADMINISTRACION",
        salario=3000.00
    )


@pytest.fixture
def mock_usuario_create(mock_personal_create):
    """Mock de datos para crear un usuario."""
    return UsuarioCreate(
        nombre="Juan",
        apellidos="Perez",
        email="juan.perez@test.com",
        password="password123",
        lista_roles=[1],
        personal=mock_personal_create
    )


@pytest.fixture
def mock_usuario_update():
    """Mock de datos para actualizar un usuario."""
    return UsuarioUpdate(
        nombre="Juan Alberto",
        apellidos="Perez Garcia",
        email="juan.alberto@test.com"
    )


@pytest.fixture
def mock_personal():
    """Mock de un personal."""
    personal = MagicMock()
    personal.id_personal = 1
    personal.nombre_completo = "Juan Perez"
    personal.dni = "12345678"
    personal.id_usuario = 1
    return personal


# ==================== TEST CLASS ====================

class TestUsuarioService:
    """Tests para UsuarioService."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura el servicio antes de cada test."""
        self.service = UsuarioService()

    # -------------------- GET ALL --------------------

    def test_get_all_retorna_lista(self, mock_db_session, mock_usuario):
        """
        Test: Obtener todos los usuarios.
        
        Resultado esperado:
        - Retorna lista con todos los usuarios
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = [mock_usuario]
            
            # Act
            resultado = self.service.get_all(mock_db_session)
            
            # Assert
            assert len(resultado) == 1
            mock_get.assert_called_once_with(mock_db_session)

    def test_get_all_lista_vacia(self, mock_db_session):
        """
        Test: Obtener usuarios cuando no hay ninguno.
        
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

    def test_get_by_id_existente(self, mock_db_session, mock_usuario):
        """
        Test: Obtener usuario por ID cuando existe.
        
        Resultado esperado:
        - Retorna el usuario solicitado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = mock_usuario
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, user_id=1)
            
            # Assert
            assert resultado.id_user == 1
            mock_get.assert_called_once_with(mock_db_session, 1)

    def test_get_by_id_no_encontrado(self, mock_db_session):
        """
        Test: Obtener usuario por ID cuando no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, user_id=999)
            
            # Assert
            assert resultado is None

    # -------------------- GET BY EMAIL --------------------

    def test_get_by_email_existente(self, mock_db_session, mock_usuario):
        """
        Test: Obtener usuario por email cuando existe.
        
        Resultado esperado:
        - Retorna el usuario con ese email
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_email') as mock_get:
            mock_get.return_value = mock_usuario
            
            # Act
            resultado = self.service.get_by_email(mock_db_session, email="test@test.com")
            
            # Assert
            assert resultado.email == "test@test.com"

    def test_get_by_email_no_encontrado(self, mock_db_session):
        """
        Test: Obtener usuario por email cuando no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_email') as mock_get:
            mock_get.return_value = None
            
            # Act
            resultado = self.service.get_by_email(mock_db_session, email="noexiste@test.com")
            
            # Assert
            assert resultado is None

    # -------------------- CREATE --------------------

    def test_create_exitoso(self, mock_db_session, mock_usuario_create, mock_usuario, mock_personal):
        """
        Test: Crear usuario exitosamente.
        
        Resultado esperado:
        - Retorna el usuario creado y info de email
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_email') as mock_email, \
             patch.object(self.service.personal_repository, 'get_by_dni') as mock_dni, \
             patch.object(self.service.rol_repository, 'get_by_id') as mock_rol, \
             patch.object(self.service.repository, 'create') as mock_create, \
             patch.object(self.service.personal_repository, 'create') as mock_create_personal, \
             patch.object(self.service.repository, 'save_roles_user') as mock_roles, \
             patch.object(self.service.email_service, 'enviar_credenciales_usuario') as mock_email_send, \
             patch('modules.Gestion_Usuarios.usuario.service.get_password_hash') as mock_hash:
            
            mock_email.return_value = None  # Email no existe
            mock_dni.return_value = None  # DNI no existe
            mock_rol.return_value = MagicMock()  # Rol existe
            mock_create.return_value = mock_usuario
            mock_create_personal.return_value = mock_personal
            mock_hash.return_value = "hashed_password"
            mock_email_send.return_value = (False, "Email no configurado")
            
            # Act
            resultado, email_info = self.service.create(mock_db_session, mock_usuario_create)
            
            # Assert
            assert resultado is not None
            assert resultado.id_user == 1
            mock_create.assert_called_once()
            mock_db_session.commit.assert_called()

    def test_create_email_duplicado(self, mock_db_session, mock_usuario_create, mock_usuario):
        """
        Test: Crear usuario con email ya existente.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_email') as mock_email:
            mock_email.return_value = mock_usuario  # Email ya existe
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.create(mock_db_session, mock_usuario_create)
            
            assert "correo electrónico ya está registrado" in str(exc_info.value)

    def test_create_email_de_usuario_anulado(self, mock_db_session, mock_usuario_create, mock_usuario):
        """
        Test: Crear usuario con email de usuario anulado.
        
        Resultado esperado:
        - Lanza ValueError con mensaje específico
        """
        # Arrange
        mock_usuario.anulado = True
        
        with patch.object(self.service.repository, 'get_by_email') as mock_email:
            mock_email.return_value = mock_usuario
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.create(mock_db_session, mock_usuario_create)
            
            assert "usuario anulado" in str(exc_info.value)

    def test_create_dni_duplicado(self, mock_db_session, mock_usuario_create, mock_personal):
        """
        Test: Crear usuario con DNI ya existente.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_email') as mock_email, \
             patch.object(self.service.personal_repository, 'get_by_dni') as mock_dni:
            mock_email.return_value = None
            mock_dni.return_value = mock_personal  # DNI ya existe
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.create(mock_db_session, mock_usuario_create)
            
            assert "DNI ya está registrado" in str(exc_info.value)

    def test_create_rol_no_existe(self, mock_db_session, mock_usuario_create):
        """
        Test: Crear usuario con rol inexistente.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_email') as mock_email, \
             patch.object(self.service.personal_repository, 'get_by_dni') as mock_dni, \
             patch.object(self.service.rol_repository, 'get_by_id') as mock_rol:
            mock_email.return_value = None
            mock_dni.return_value = None
            mock_rol.return_value = None  # Rol no existe
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.create(mock_db_session, mock_usuario_create)
            
            assert "rol con ID" in str(exc_info.value)

    def test_create_hashea_password(self, mock_db_session, mock_usuario_create, mock_usuario, mock_personal):
        """
        Test: Verificar que la contraseña se hashea antes de guardar.
        
        Resultado esperado:
        - Password se hashea correctamente
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_email') as mock_email, \
             patch.object(self.service.personal_repository, 'get_by_dni') as mock_dni, \
             patch.object(self.service.rol_repository, 'get_by_id') as mock_rol, \
             patch.object(self.service.repository, 'create') as mock_create, \
             patch.object(self.service.personal_repository, 'create') as mock_create_personal, \
             patch.object(self.service.repository, 'save_roles_user') as mock_roles, \
             patch.object(self.service.email_service, 'enviar_credenciales_usuario') as mock_email_send, \
             patch('modules.Gestion_Usuarios.usuario.service.get_password_hash') as mock_hash:
            
            mock_email.return_value = None
            mock_dni.return_value = None
            mock_rol.return_value = MagicMock()
            mock_create.return_value = mock_usuario
            mock_create_personal.return_value = mock_personal
            mock_hash.return_value = "hashed_password_123"
            mock_email_send.return_value = (False, "No configurado")
            
            # Act
            self.service.create(mock_db_session, mock_usuario_create)
            
            # Assert
            mock_hash.assert_called_once_with("password123")

    # -------------------- UPDATE --------------------

    def test_update_exitoso(self, mock_db_session, mock_usuario_update, mock_usuario):
        """
        Test: Actualizar usuario existente.
        
        Resultado esperado:
        - Retorna el usuario actualizado
        """
        # Arrange
        mock_usuario.nombre = "Juan Alberto"
        
        with patch.object(self.service.repository, 'get_by_id') as mock_get, \
             patch.object(self.service.repository, 'update') as mock_update:
            mock_get.return_value = mock_usuario
            mock_update.return_value = mock_usuario
            
            # Act
            resultado = self.service.update(mock_db_session, user_id=1, user_update=mock_usuario_update)
            
            # Assert
            assert resultado.nombre == "Juan Alberto"
            mock_db_session.commit.assert_called()

    def test_update_usuario_no_existe(self, mock_db_session, mock_usuario_update):
        """
        Test: Actualizar usuario que no existe.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.update(mock_db_session, user_id=999, user_update=mock_usuario_update)
            
            assert "usuario no existe" in str(exc_info.value)

    def test_update_rol_no_existe(self, mock_db_session, mock_usuario):
        """
        Test: Actualizar usuario con rol inexistente.
        
        Resultado esperado:
        - Lanza ValueError y hace rollback
        """
        # Arrange
        update_data = UsuarioUpdate(lista_roles=[999])
        
        with patch.object(self.service.repository, 'get_by_id') as mock_get, \
             patch.object(self.service.rol_repository, 'get_by_id') as mock_rol:
            mock_get.return_value = mock_usuario
            mock_rol.return_value = None  # Rol no existe
            
            # Act & Assert
            with pytest.raises(ValueError) as exc_info:
                self.service.update(mock_db_session, user_id=1, user_update=update_data)
            
            assert "rol con ID" in str(exc_info.value)
            mock_db_session.rollback.assert_called()

    def test_update_hashea_nueva_password(self, mock_db_session, mock_usuario):
        """
        Test: Hashear contraseña cuando se actualiza.
        
        Resultado esperado:
        - Nueva password se hashea
        """
        # Arrange
        update_data = UsuarioUpdate(password="nueva_password")
        
        with patch.object(self.service.repository, 'get_by_id') as mock_get, \
             patch.object(self.service.repository, 'update') as mock_update, \
             patch('modules.Gestion_Usuarios.usuario.service.get_password_hash') as mock_hash:
            mock_get.return_value = mock_usuario
            mock_hash.return_value = "hashed_nueva_password"
            
            # Act
            self.service.update(mock_db_session, user_id=1, user_update=update_data)
            
            # Assert
            mock_hash.assert_called_once_with("nueva_password")

    def test_update_sincroniza_estado_con_personal(self, mock_db_session, mock_usuario, mock_personal):
        """
        Test: Sincronizar estado anulado con personal.
        
        Resultado esperado:
        - Actualiza estado de personal cuando se anula usuario
        """
        # Arrange
        update_data = UsuarioUpdate(anulado=True)
        
        with patch.object(self.service.repository, 'get_by_id') as mock_get, \
             patch.object(self.service.repository, 'update') as mock_update, \
             patch.object(self.service.personal_repository, 'get_by_usuario_id') as mock_pers, \
             patch.object(self.service.personal_repository, 'update_estado') as mock_estado:
            mock_get.return_value = mock_usuario
            mock_pers.return_value = mock_personal
            
            # Act
            self.service.update(mock_db_session, user_id=1, user_update=update_data)
            
            # Assert
            mock_estado.assert_called_once_with(mock_db_session, mock_personal.id_personal, True)

    # -------------------- DELETE --------------------

    def test_delete_exitoso(self, mock_db_session, mock_personal):
        """
        Test: Eliminar (anular) usuario exitosamente.
        
        Resultado esperado:
        - Retorna True y sincroniza con personal
        """
        # Arrange
        with patch.object(self.service.personal_repository, 'get_by_usuario_id') as mock_pers, \
             patch.object(self.service.personal_repository, 'update_estado') as mock_estado, \
             patch.object(self.service.repository, 'delete') as mock_delete:
            mock_pers.return_value = mock_personal
            mock_delete.return_value = True
            
            # Act
            resultado = self.service.delete(mock_db_session, user_id=1)
            
            # Assert
            assert resultado is True
            mock_estado.assert_called_once()

    def test_delete_sin_personal_asociado(self, mock_db_session):
        """
        Test: Eliminar usuario sin personal asociado.
        
        Resultado esperado:
        - Se elimina correctamente sin error
        """
        # Arrange
        with patch.object(self.service.personal_repository, 'get_by_usuario_id') as mock_pers, \
             patch.object(self.service.repository, 'delete') as mock_delete:
            mock_pers.return_value = None  # Sin personal
            mock_delete.return_value = True
            
            # Act
            resultado = self.service.delete(mock_db_session, user_id=1)
            
            # Assert
            assert resultado is True

    # -------------------- UPDATE LAST ACCESS --------------------

    def test_update_last_access(self, mock_db_session, mock_usuario):
        """
        Test: Actualizar último acceso del usuario.
        
        Resultado esperado:
        - Actualiza fecha de último acceso
        """
        # Arrange
        mock_usuario.ultimo_acceso = datetime.now()
        
        with patch.object(self.service.repository, 'update_last_access') as mock_update:
            mock_update.return_value = mock_usuario
            
            # Act
            resultado = self.service.update_last_access(mock_db_session, user_id=1)
            
            # Assert
            assert resultado is not None
            mock_update.assert_called_once_with(mock_db_session, 1)
