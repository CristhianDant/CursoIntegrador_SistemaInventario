"""
Pruebas de integración para el módulo de autenticación (Login).

Tests:
1. Login exitoso con credenciales válidas
2. Login fallido con contraseña incorrecta
3. Login fallido con email inexistente
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestLoginIntegration:
    """Pruebas de integración para el endpoint de login."""

    def test_login_exitoso_con_credenciales_validas(self, client: TestClient, usuario_admin):
        """
        Test: Login exitoso retorna token JWT y datos del usuario.
        
        Dado: Un usuario admin existe en la base de datos
        Cuando: Se hace POST /api/v1/login con credenciales correctas
        Entonces: Se retorna status 200 con token y datos del usuario
        """
        # Arrange
        login_data = {
            "email": "admin@test.com",
            "password": "Admin123!"
        }
        
        # Act
        response = client.post("/api/v1/login", json=login_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estructura de respuesta
        assert "data" in data
        assert "token" in data["data"]
        assert "access_token" in data["data"]["token"]
        assert "token_type" in data["data"]["token"]
        assert data["data"]["token"]["token_type"] == "bearer"
        
        # Verificar datos del usuario
        assert data["data"]["nombre"] == "Admin"
        assert data["data"]["email"] == "admin@test.com"
        assert "roles" in data["data"]
        assert len(data["data"]["roles"]) > 0

    def test_login_fallido_con_password_incorrecta(self, client: TestClient, usuario_admin):
        """
        Test: Login con contraseña incorrecta retorna error 401.
        
        Dado: Un usuario existe en la base de datos
        Cuando: Se hace POST /api/v1/login con contraseña incorrecta
        Entonces: Se retorna status 401 (no autorizado)
        """
        # Arrange
        login_data = {
            "email": "admin@test.com",
            "password": "ContraseñaIncorrecta123!"
        }
        
        # Act
        response = client.post("/api/v1/login", json=login_data)
        
        # Assert - La API retorna 401 Unauthorized
        assert response.status_code == 401

    def test_login_fallido_con_email_inexistente(self, client: TestClient, db_session):
        """
        Test: Login con email que no existe retorna error.
        
        Dado: No existe usuario con el email proporcionado
        Cuando: Se hace POST /api/v1/login con email inexistente
        Entonces: Se retorna error de autenticación
        """
        # Arrange
        login_data = {
            "email": "noexiste@test.com",
            "password": "Cualquier123!"
        }
        
        # Act
        response = client.post("/api/v1/login", json=login_data)
        
        # Assert - La API retorna 401 Unauthorized
        assert response.status_code == 401

    def test_login_fallido_con_email_formato_invalido(self, client: TestClient, db_session):
        """
        Test: Login con email en formato inválido retorna error de validación.
        
        Dado: Se proporciona un email con formato inválido
        Cuando: Se hace POST /api/v1/login
        Entonces: Se retorna error de validación (422)
        """
        # Arrange
        login_data = {
            "email": "email-invalido",
            "password": "Cualquier123!"
        }
        
        # Act
        response = client.post("/api/v1/login", json=login_data)
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity - validación de Pydantic
