"""
Tests unitarios para ProduccionService - Lógica de negocio de producción.
Usa mocks para simular el repositorio y la base de datos.
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from modules.gestion_almacen_inusmos.produccion.service import ProduccionService
from modules.gestion_almacen_inusmos.produccion.schemas import ProduccionRequest


class TestProduccionServiceValidarStock:
    """Tests para validación de stock en ProduccionService."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup ejecutado antes de cada test."""
        self.service = ProduccionService()
    
    def test_validar_stock_receta_con_stock_suficiente(
        self, 
        mock_db_session, 
        mock_receta_data
    ):
        """
        Test: Validar stock cuando HAY suficiente stock para producir.
        
        Escenario:
        - Receta requiere 2 kg de harina y 0.05 kg de sal por batch
        - Solicitud: producir 5 batches
        - Stock disponible: harina=50kg, sal=10kg
        
        Resultado esperado:
        - puede_producir = True
        - insumos marcados como es_suficiente = True
        - mensaje de éxito
        """
        # Arrange
        with patch.object(self.service.repository, 'get_receta_con_insumos') as mock_get_receta, \
             patch.object(self.service.repository, 'get_stock_disponible_insumo') as mock_get_stock:
            
            mock_get_receta.return_value = mock_receta_data
            # Mock de stock disponible para cada insumo
            mock_get_stock.side_effect = [Decimal("50.00"), Decimal("10.00")]
            
            # Act
            resultado = self.service.validar_stock_receta(
                db=mock_db_session,
                id_receta=1,
                cantidad_batch=Decimal("5.00")
            )
            
            # Assert
            assert resultado.puede_producir is True
            assert len(resultado.insumos) == 2
            
            # Verificar primer insumo (harina)
            assert resultado.insumos[0].cantidad_requerida == Decimal("10.00")  # 5 batches * 2 kg
            assert resultado.insumos[0].stock_disponible == Decimal("50.00")
            assert resultado.insumos[0].es_suficiente is True
            
            # Verificar segundo insumo (sal)
            assert resultado.insumos[1].cantidad_requerida == Decimal("0.25")  # 5 batches * 0.05 kg
            assert resultado.insumos[1].stock_disponible == Decimal("10.00")
            assert resultado.insumos[1].es_suficiente is True
            
            assert "Stock suficiente" in resultado.mensaje
            
            # Verificar que se llamaron los métodos correctos
            mock_get_receta.assert_called_once_with(mock_db_session, 1)
            assert mock_get_stock.call_count == 2
    
    def test_validar_stock_receta_con_stock_insuficiente(
        self, 
        mock_db_session, 
        mock_receta_data
    ):
        """
        Test: Validar stock cuando NO HAY suficiente stock.
        
        Escenario:
        - Receta requiere 2 kg de harina por batch
        - Solicitud: producir 30 batches (60 kg necesarios)
        - Stock disponible: solo 50 kg
        
        Resultado esperado:
        - puede_producir = False
        - insumos marcados como es_suficiente = False
        - mensaje indicando falta de stock
        """
        # Arrange
        with patch.object(self.service.repository, 'get_receta_con_insumos') as mock_get_receta, \
             patch.object(self.service.repository, 'get_stock_disponible_insumo') as mock_get_stock:
            
            mock_get_receta.return_value = mock_receta_data
            # Stock insuficiente para harina, suficiente para sal
            mock_get_stock.side_effect = [Decimal("50.00"), Decimal("10.00")]
            
            # Act
            resultado = self.service.validar_stock_receta(
                db=mock_db_session,
                id_receta=1,
                cantidad_batch=Decimal("30.00")  # Requiere 60 kg de harina
            )
            
            # Assert
            assert resultado.puede_producir is False
            
            # Verificar primer insumo (harina) - INSUFICIENTE
            assert resultado.insumos[0].cantidad_requerida == Decimal("60.00")
            assert resultado.insumos[0].stock_disponible == Decimal("50.00")
            assert resultado.insumos[0].es_suficiente is False
            
            # Verificar segundo insumo (sal) - SUFICIENTE
            assert resultado.insumos[1].cantidad_requerida == Decimal("1.50")
            assert resultado.insumos[1].stock_disponible == Decimal("10.00")
            assert resultado.insumos[1].es_suficiente is True
            
            assert "Stock insuficiente" in resultado.mensaje
            assert "Harina de Trigo" in resultado.mensaje
    
    def test_validar_stock_receta_no_encontrada(self, mock_db_session):
        """
        Test: Validar stock cuando la receta NO existe.
        
        Resultado esperado:
        - Lanza HTTPException con código 404
        - Mensaje: "Receta no encontrada"
        """
        # Arrange
        with patch.object(self.service.repository, 'get_receta_con_insumos') as mock_get_receta:
            mock_get_receta.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.validar_stock_receta(
                    db=mock_db_session,
                    id_receta=99999,
                    cantidad_batch=Decimal("1.00")
                )
            
            assert exc_info.value.status_code == 404
            assert "Receta no encontrada" in str(exc_info.value.detail)
    
    def test_validar_stock_ignora_insumos_opcionales(
        self, 
        mock_db_session, 
        mock_receta_data
    ):
        """
        Test: Validar que los insumos opcionales NO se validan.
        
        Escenario:
        - Receta tiene 1 insumo obligatorio y 1 opcional
        - Insumo opcional no tiene stock
        
        Resultado esperado:
        - puede_producir = True (ignora el opcional)
        - Solo valida insumos NO opcionales
        """
        # Arrange
        receta_con_opcionales = mock_receta_data.copy()
        receta_con_opcionales["insumos"].append({
            "id_insumo": 3,
            "codigo_insumo": "INS003",
            "nombre_insumo": "Colorante (Opcional)",
            "unidad_medida": "ml",
            "cantidad_por_rendimiento": Decimal("0.10"),
            "es_opcional": True  # OPCIONAL
        })
        
        with patch.object(self.service.repository, 'get_receta_con_insumos') as mock_get_receta, \
             patch.object(self.service.repository, 'get_stock_disponible_insumo') as mock_get_stock:
            
            mock_get_receta.return_value = receta_con_opcionales
            # Stock para insumos obligatorios (opcionales no se consultan)
            mock_get_stock.side_effect = [Decimal("50.00"), Decimal("10.00")]
            
            # Act
            resultado = self.service.validar_stock_receta(
                db=mock_db_session,
                id_receta=1,
                cantidad_batch=Decimal("5.00")
            )
            
            # Assert
            assert resultado.puede_producir is True
            # Solo debe validar los 2 insumos obligatorios
            assert len(resultado.insumos) == 2
            # El colorante opcional NO debe aparecer en la lista
            nombres_validados = [ins.nombre_insumo for ins in resultado.insumos]
            assert "Colorante (Opcional)" not in nombres_validados


class TestProduccionServiceEjecutar:
    """Tests para ejecución de producción."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup ejecutado antes de cada test."""
        self.service = ProduccionService()
    
    def test_ejecutar_produccion_exitoso(
        self, 
        mock_db_session, 
        mock_receta_data,
        mock_produccion_creada
    ):
        """
        Test: Ejecutar producción con stock suficiente.
        
        Escenario:
        - Receta produce 10 unidades por batch
        - Requiere 2 kg de harina por batch
        - Stock disponible: 50 kg
        - Producir 5 batches
        
        Resultado esperado:
        - success = True
        - cantidad_producida = 50 unidades (5 batches * 10)
        - Se descuentan 10 kg de harina
        - Se crean movimientos de entrada/salida
        """
        # Arrange
        request = ProduccionRequest(
            id_receta=1,
            cantidad_batch=Decimal("5.00"),
            id_user=1,
            observaciones="Test producción"
        )
        
        with patch.object(self.service, 'validar_stock_receta') as mock_validar, \
             patch.object(self.service.repository, 'get_receta_con_insumos') as mock_get_receta, \
             patch.object(self.service.repository, 'crear_produccion') as mock_crear_prod, \
             patch.object(self.service.repository, 'descontar_insumo_fefo') as mock_descontar, \
             patch.object(self.service.repository, 'get_id_producto_de_receta') as mock_get_producto, \
             patch.object(self.service.repository, 'get_stock_producto_terminado') as mock_get_stock_pt, \
             patch.object(self.service.repository, 'incrementar_stock_producto_terminado') as mock_incrementar, \
             patch.object(self.service.repository, 'crear_movimiento_producto_terminado') as mock_crear_mov, \
             patch.object(self.service.repository, '_reset_contador_movimientos') as mock_reset:
            
            # Mock validación exitosa
            mock_validacion = Mock()
            mock_validacion.puede_producir = True
            mock_validar.return_value = mock_validacion
            
            mock_get_receta.return_value = mock_receta_data
            mock_crear_prod.return_value = mock_produccion_creada
            mock_descontar.return_value = 2  # 2 movimientos por insumo
            mock_get_producto.return_value = 1  # id_producto
            mock_get_stock_pt.return_value = Decimal("0.00")
            mock_incrementar.return_value = Decimal("50.00")
            
            # Act
            resultado = self.service.ejecutar_produccion(
                db=mock_db_session,
                request=request
            )
            
            # Assert
            assert resultado.success is True
            assert resultado.cantidad_batch == Decimal("5.00")
            assert resultado.cantidad_producida == Decimal("50.00")  # 5 * 10
            assert "ejecutada correctamente" in resultado.mensaje
            
            # Verificar que se llamaron los métodos en orden
            mock_validar.assert_called_once()
            mock_crear_prod.assert_called_once()
            assert mock_descontar.call_count == 2  # 2 insumos
            mock_incrementar.assert_called_once()
            mock_crear_mov.assert_called_once()
            mock_db_session.commit.assert_called_once()
            mock_reset.assert_called()
    
    def test_ejecutar_produccion_sin_stock_falla(
        self, 
        mock_db_session
    ):
        """
        Test: Ejecutar producción SIN stock suficiente debe fallar.
        
        Resultado esperado:
        - Lanza HTTPException con código 400
        - Mensaje: "Stock insuficiente"
        - NO se crea ningún registro (rollback implícito)
        """
        # Arrange
        request = ProduccionRequest(
            id_receta=1,
            cantidad_batch=Decimal("30.00"),
            id_user=1,
            observaciones="Sin stock"
        )
        
        with patch.object(self.service, 'validar_stock_receta') as mock_validar:
            # Mock validación FALLIDA
            mock_validacion = Mock()
            mock_validacion.puede_producir = False
            mock_validacion.mensaje = "Stock insuficiente para: Harina de Trigo"
            mock_validar.return_value = mock_validacion
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.ejecutar_produccion(
                    db=mock_db_session,
                    request=request
                )
            
            assert exc_info.value.status_code == 400
            assert "Stock insuficiente" in str(exc_info.value.detail)
            
            # Verificar que NO se hizo commit
            mock_db_session.commit.assert_not_called()
    
    def test_ejecutar_produccion_error_rollback(
        self, 
        mock_db_session, 
        mock_receta_data,
        mock_produccion_creada
    ):
        """
        Test: Si ocurre un error durante la producción, debe hacer rollback.
        
        Escenario:
        - Error al descontar insumos
        
        Resultado esperado:
        - Lanza HTTPException con código 500
        - Se hace rollback de la transacción
        - Se resetea el contador de movimientos
        """
        # Arrange
        request = ProduccionRequest(
            id_receta=1,
            cantidad_batch=Decimal("5.00"),
            id_user=1,
            observaciones="Test error"
        )
        
        with patch.object(self.service, 'validar_stock_receta') as mock_validar, \
             patch.object(self.service.repository, 'get_receta_con_insumos') as mock_get_receta, \
             patch.object(self.service.repository, 'crear_produccion') as mock_crear_prod, \
             patch.object(self.service.repository, 'descontar_insumo_fefo') as mock_descontar, \
             patch.object(self.service.repository, '_reset_contador_movimientos') as mock_reset:
            
            mock_validacion = Mock()
            mock_validacion.puede_producir = True
            mock_validar.return_value = mock_validacion
            
            mock_get_receta.return_value = mock_receta_data
            mock_crear_prod.return_value = mock_produccion_creada
            
            # Simular error al descontar
            mock_descontar.side_effect = Exception("Error simulado al descontar")
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.ejecutar_produccion(
                    db=mock_db_session,
                    request=request
                )
            
            assert exc_info.value.status_code == 500
            assert "Error al ejecutar producción" in str(exc_info.value.detail)
            
            # Verificar rollback
            mock_db_session.rollback.assert_called_once()
            # Verificar reset del contador
            mock_reset.assert_called()


class TestProduccionServiceHistorial:
    """Tests para historial y trazabilidad de producciones."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup ejecutado antes de cada test."""
        self.service = ProduccionService()
    
    def test_get_historial_producciones(
        self, 
        mock_db_session,
        mock_historial_producciones
    ):
        """
        Test: Obtener historial de producciones.
        
        Resultado esperado:
        - Retorna lista de producciones con sus datos
        - Total correcto
        """
        # Arrange
        with patch.object(self.service.repository, 'get_historial_producciones') as mock_get_historial:
            mock_get_historial.return_value = mock_historial_producciones
            
            # Act
            resultado = self.service.get_historial_producciones(
                db=mock_db_session,
                limit=50,
                offset=0
            )
            
            # Assert
            assert resultado.total == 2
            assert len(resultado.producciones) == 2
            assert resultado.producciones[0].numero_produccion == "PROD-20251201-001"
            assert resultado.producciones[0].cantidad_producida == Decimal("50.00")
            
            mock_get_historial.assert_called_once_with(mock_db_session, 50, 0)
    
    def test_get_trazabilidad_produccion(
        self, 
        mock_db_session,
        mock_trazabilidad_produccion
    ):
        """
        Test: Obtener trazabilidad completa de una producción.
        
        Resultado esperado:
        - Retorna datos de producción, receta, producto e insumos
        - Contiene información de movimientos
        """
        # Arrange
        with patch.object(self.service.repository, 'get_trazabilidad_produccion') as mock_get_traza:
            mock_get_traza.return_value = mock_trazabilidad_produccion
            
            # Act
            resultado = self.service.get_trazabilidad_produccion(
                db=mock_db_session,
                id_produccion=1
            )
            
            # Assert
            assert resultado.produccion.id_produccion == 1
            assert resultado.produccion.cantidad_batch == Decimal("5.00")
            assert resultado.receta.nombre_receta == "Pan Francés"
            assert resultado.producto_terminado.nombre_producto == "Pan Francés"
            assert len(resultado.insumos_consumidos) == 1
            assert resultado.total_lotes_consumidos == 1
            
            # Verificar datos del insumo consumido
            insumo = resultado.insumos_consumidos[0]
            assert insumo.nombre_insumo == "Harina de Trigo"
            assert insumo.cantidad_consumida == Decimal("10.00")
            
            mock_get_traza.assert_called_once_with(mock_db_session, 1)
    
    def test_get_trazabilidad_produccion_no_encontrada(
        self, 
        mock_db_session
    ):
        """
        Test: Obtener trazabilidad de producción inexistente.
        
        Resultado esperado:
        - Lanza HTTPException con código 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_trazabilidad_produccion') as mock_get_traza:
            mock_get_traza.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_trazabilidad_produccion(
                    db=mock_db_session,
                    id_produccion=99999
                )
            
            assert exc_info.value.status_code == 404
            assert "no encontrada" in str(exc_info.value.detail).lower()
