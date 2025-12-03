"""
Pruebas de integración para el módulo de Proveedores.

Tests:
1. Crear proveedor - CRUD Create
2. Listar proveedores - CRUD Read (list)
3. Obtener proveedor por ID - CRUD Read (single)
4. Actualizar proveedor - CRUD Update
5. Eliminar proveedor (soft delete) - CRUD Delete
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestProveedoresIntegration:
    """Pruebas de integración CRUD completo para proveedores."""

    def test_crear_proveedor_exitoso(self, client: TestClient, db_session):
        """
        Test: Crear un nuevo proveedor exitosamente.
        
        Dado: No existe el proveedor en la base de datos
        Cuando: Se hace POST /api/v1/proveedores con datos válidos
        Entonces: Se crea el proveedor y se retorna con ID asignado
        """
        # Arrange
        proveedor_data = {
            "nombre": "Distribuidora Lima S.A.C.",
            "ruc_dni": "20456789123",
            "numero_contacto": "987654321",
            "email_contacto": "ventas@distribuidora.com",
            "direccion_fiscal": "Jr. Comercio 789, Lima"
        }
        
        # Act
        response = client.post("/api/v1/proveedores/", json=proveedor_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert data["data"]["nombre"] == proveedor_data["nombre"]
        assert data["data"]["ruc_dni"] == proveedor_data["ruc_dni"]
        assert data["data"]["email_contacto"] == proveedor_data["email_contacto"]
        assert "id_proveedor" in data["data"]
        assert data["data"]["anulado"] == False

    def test_listar_proveedores(self, client: TestClient, proveedor_base):
        """
        Test: Listar todos los proveedores.
        
        Dado: Existe al menos un proveedor en la base de datos
        Cuando: Se hace GET /api/v1/proveedores
        Entonces: Se retorna lista con los proveedores
        """
        # Act
        response = client.get("/api/v1/proveedores/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        
        # Verificar que el proveedor base está en la lista
        proveedores_nombres = [p["nombre"] for p in data["data"]]
        assert proveedor_base.nombre in proveedores_nombres

    def test_obtener_proveedor_por_id(self, client: TestClient, proveedor_base):
        """
        Test: Obtener un proveedor específico por su ID.
        
        Dado: Existe un proveedor con ID conocido
        Cuando: Se hace GET /api/v1/proveedores/{id}
        Entonces: Se retorna el proveedor con todos sus datos
        """
        # Act
        response = client.get(f"/api/v1/proveedores/{proveedor_base.id_proveedor}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert data["data"]["id_proveedor"] == proveedor_base.id_proveedor
        assert data["data"]["nombre"] == proveedor_base.nombre
        assert data["data"]["ruc_dni"] == proveedor_base.ruc_dni

    def test_obtener_proveedor_inexistente(self, client: TestClient, db_session):
        """
        Test: Obtener proveedor con ID que no existe retorna 404.
        
        Dado: No existe proveedor con el ID proporcionado
        Cuando: Se hace GET /api/v1/proveedores/{id_inexistente}
        Entonces: Se retorna error 404 (not found)
        """
        # Act
        response = client.get("/api/v1/proveedores/99999")
        
        # Assert - La API retorna 404 Not Found
        assert response.status_code == 404

    def test_actualizar_proveedor(self, client: TestClient, proveedor_base):
        """
        Test: Actualizar datos de un proveedor existente.
        
        Dado: Existe un proveedor en la base de datos
        Cuando: Se hace PUT /api/v1/proveedores/{id} con datos actualizados
        Entonces: El proveedor se actualiza correctamente
        """
        # Arrange
        datos_actualizados = {
            "nombre": "Proveedor Actualizado S.A.",
            "numero_contacto": "111222333"
        }
        
        # Act
        response = client.put(
            f"/api/v1/proveedores/{proveedor_base.id_proveedor}",
            json=datos_actualizados
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert data["data"]["nombre"] == datos_actualizados["nombre"]
        assert data["data"]["numero_contacto"] == datos_actualizados["numero_contacto"]
        # Los campos no actualizados deben mantenerse
        assert data["data"]["ruc_dni"] == proveedor_base.ruc_dni

    def test_eliminar_proveedor_soft_delete(self, client: TestClient, proveedor_base):
        """
        Test: Eliminar proveedor (soft delete - marca como anulado).
        
        Dado: Existe un proveedor activo
        Cuando: Se hace DELETE /api/v1/proveedores/{id}
        Entonces: El proveedor se marca como anulado (soft delete)
        """
        # Act
        response = client.delete(f"/api/v1/proveedores/{proveedor_base.id_proveedor}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verificar que se eliminó (soft delete)
        assert "data" in data
        # El proveedor debe estar marcado como anulado
        assert data["data"]["anulado"] == True
