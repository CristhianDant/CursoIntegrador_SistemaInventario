"""
Pruebas de integración para el módulo de Productos Terminados.

Tests:
1. Crear producto terminado
2. Listar productos terminados
3. Obtener producto por ID
4. Actualizar precio de venta
5. Eliminar producto (soft delete)
"""
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal


@pytest.mark.integration
class TestProductosTerminadosIntegration:
    """Pruebas de integración para productos terminados."""

    def test_crear_producto_terminado_exitoso(self, client: TestClient, db_session):
        """
        Test: Crear un nuevo producto terminado.
        
        Dado: No existe el producto en la base de datos
        Cuando: Se hace POST /api/v1/productos_terminados con datos válidos
        Entonces: Se crea el producto con stock_actual en 0
        """
        # Arrange
        producto_data = {
            "codigo_producto": "PAN001",
            "nombre": "Pan Francés",
            "descripcion": "Pan francés tradicional 100g",
            "unidad_medida": "UNIDAD",
            "stock_minimo": 20,
            "vida_util_dias": 2,
            "precio_venta": 1.50
        }
        
        # Act
        response = client.post("/api/v1/productos_terminados/", json=producto_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert data["data"]["codigo_producto"] == producto_data["codigo_producto"]
        assert data["data"]["nombre"].lower() == producto_data["nombre"].lower()
        assert "id_producto" in data["data"]
        # Stock inicial debe ser 0
        assert float(data["data"]["stock_actual"]) == 0.0
        assert data["data"]["anulado"] == False

    def test_listar_productos_terminados(self, client: TestClient, producto_terminado_base):
        """
        Test: Listar todos los productos terminados.
        
        Dado: Existe al menos un producto en la base de datos
        Cuando: Se hace GET /api/v1/productos_terminados
        Entonces: Se retorna lista con los productos
        """
        # Act
        response = client.get("/api/v1/productos_terminados/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1
        
        # Verificar que el producto base está en la lista
        productos_codigos = [p["codigo_producto"] for p in data["data"]]
        assert producto_terminado_base.codigo_producto in productos_codigos

    def test_obtener_producto_por_id(self, client: TestClient, producto_terminado_base):
        """
        Test: Obtener un producto específico por su ID.
        
        Dado: Existe un producto con ID conocido
        Cuando: Se hace GET /api/v1/productos_terminados/{id}
        Entonces: Se retorna el producto con todos sus datos
        """
        # Act
        response = client.get(f"/api/v1/productos_terminados/{producto_terminado_base.id_producto}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        assert data["data"]["id_producto"] == producto_terminado_base.id_producto
        assert data["data"]["nombre"] == producto_terminado_base.nombre
        assert data["data"]["codigo_producto"] == producto_terminado_base.codigo_producto

    def test_actualizar_precio_venta_producto(self, client: TestClient, producto_terminado_base):
        """
        Test: Actualizar el precio de venta de un producto.
        
        Dado: Existe un producto en la base de datos
        Cuando: Se hace PUT /api/v1/productos_terminados/{id} con nuevo precio
        Entonces: El precio se actualiza correctamente
        """
        # Arrange
        datos_actualizados = {
            "codigo_producto": producto_terminado_base.codigo_producto,
            "nombre": producto_terminado_base.nombre,
            "unidad_medida": producto_terminado_base.unidad_medida,
            "precio_venta": 7.50  # Nuevo precio
        }
        
        # Act
        response = client.put(
            f"/api/v1/productos_terminados/{producto_terminado_base.id_producto}",
            json=datos_actualizados
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        # Verificar nuevo precio
        assert float(data["data"]["precio_venta"]) == 7.50

    def test_eliminar_producto_terminado(self, client: TestClient, producto_terminado_base):
        """
        Test: Eliminar producto terminado (soft delete).
        
        Dado: Existe un producto activo
        Cuando: Se hace DELETE /api/v1/productos_terminados/{id}
        Entonces: El producto se marca como eliminado
        """
        # Act
        response = client.delete(f"/api/v1/productos_terminados/{producto_terminado_base.id_producto}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        assert "data" in data
        # Verificar mensaje de eliminación exitosa
        assert "eliminado" in str(data["data"]).lower() or data["data"].get("detail")

    def test_obtener_producto_inexistente(self, client: TestClient, db_session):
        """
        Test: Obtener producto con ID que no existe retorna error.
        
        Dado: No existe producto con el ID proporcionado
        Cuando: Se hace GET /api/v1/productos_terminados/{id_inexistente}
        Entonces: Se retorna error (not found)
        """
        # Act
        response = client.get("/api/v1/productos_terminados/99999")
        
        # Assert - La API retorna 404 Not Found
        assert response.status_code == 404
