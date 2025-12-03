"""
Tests unitarios para PromocionService.

Este módulo contiene tests para validar el comportamiento del servicio de promociones
utilizando mocks para aislar la lógica del servicio.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import date, datetime, timedelta

from modules.promociones.service import PromocionService
from modules.promociones.model import Promocion, EstadoPromocion, TipoPromocion
from modules.promociones.schemas import (
    PromocionCreate, PromocionUpdate, PromocionResponse,
    TipoPromocionEnum, EstadoPromocionEnum, SugerenciaPromocion
)


# ==================== FIXTURES ADICIONALES ====================

@pytest.fixture
def mock_promocion_db():
    """Mock de una promoción del modelo de base de datos."""
    promocion = MagicMock()
    promocion.id_promocion = 1
    promocion.codigo_promocion = "PROMO001"
    promocion.titulo = "Descuento 20%"
    promocion.descripcion = "Promoción de prueba"
    promocion.tipo_promocion = TipoPromocion.DESCUENTO
    promocion.estado = EstadoPromocion.ACTIVA
    promocion.id_producto = 1
    promocion.porcentaje_descuento = Decimal("20.00")
    promocion.precio_promocional = None
    promocion.cantidad_minima = 1
    promocion.fecha_inicio = date.today()
    promocion.fecha_fin = date.today() + timedelta(days=7)
    promocion.dias_hasta_vencimiento = 5
    promocion.motivo = "Promoción de prueba"
    promocion.ahorro_potencial = Decimal("100.00")
    promocion.veces_aplicada = 0
    promocion.fecha_creacion = datetime.now()
    promocion.fecha_modificacion = datetime.now()
    promocion.creado_automaticamente = False
    promocion.anulado = False
    promocion.producto = MagicMock(nombre="Producto Test", stock_actual=Decimal("50"), precio_venta=Decimal("25"))
    promocion.productos_combo = []
    return promocion


@pytest.fixture
def mock_promocion_create():
    """Mock de datos para crear una promoción."""
    return PromocionCreate(
        titulo="Nueva Promoción",
        descripcion="Descripción de prueba",
        tipo_promocion=TipoPromocionEnum.DESCUENTO,
        id_producto=1,
        porcentaje_descuento=15.0,
        cantidad_minima=1,
        fecha_inicio=date.today(),
        fecha_fin=date.today() + timedelta(days=7)
    )


@pytest.fixture
def mock_promocion_update():
    """Mock de datos para actualizar una promoción."""
    return PromocionUpdate(
        titulo="Promoción Actualizada",
        porcentaje_descuento=25.0
    )


@pytest.fixture
def mock_sugerencia():
    """Mock de una sugerencia de promoción."""
    return SugerenciaPromocion(
        id_producto=1,
        nombre_producto="Producto Por Vencer",
        stock_actual=20.0,
        precio_venta=15.0,
        dias_hasta_vencimiento=3,
        tipo_sugerido=TipoPromocionEnum.DESCUENTO,
        titulo_sugerido="Oferta Especial - Producto Por Vencer",
        descripcion_sugerida="Aproveche 30% de descuento",
        descuento_sugerido=30.0,
        ahorro_potencial=90.0,
        urgencia="ALTA"
    )


# ==================== TEST CLASS ====================

class TestPromocionService:
    """Tests para PromocionService."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_db_session):
        """Configura el servicio antes de cada test."""
        self.service = PromocionService(mock_db_session)
        self.mock_db = mock_db_session

    # -------------------- GET ALL --------------------

    def test_get_all_retorna_lista(self, mock_promocion_db):
        """
        Test: Obtener todas las promociones.
        
        Resultado esperado:
        - Retorna lista de PromocionResponse
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = [mock_promocion_db]
            
            # Act
            resultado = self.service.get_all()
            
            # Assert
            assert len(resultado) == 1
            assert isinstance(resultado[0], PromocionResponse)
            mock_get.assert_called_once()

    def test_get_all_lista_vacia(self):
        """
        Test: Obtener promociones cuando no hay ninguna.
        
        Resultado esperado:
        - Retorna lista vacía
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = []
            
            # Act
            resultado = self.service.get_all()
            
            # Assert
            assert resultado == []

    # -------------------- GET BY ID --------------------

    def test_get_by_id_existente(self, mock_promocion_db):
        """
        Test: Obtener promoción por ID cuando existe.
        
        Resultado esperado:
        - Retorna la promoción como PromocionResponse
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.get_by_id(promocion_id=1)
            
            # Assert
            assert resultado is not None
            assert resultado.id_promocion == 1
            mock_get.assert_called_once_with(1)

    def test_get_by_id_no_encontrado(self):
        """
        Test: Obtener promoción por ID cuando no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act
            resultado = self.service.get_by_id(promocion_id=999)
            
            # Assert
            assert resultado is None

    # -------------------- GET ACTIVAS --------------------

    def test_get_activas_retorna_solo_activas(self, mock_promocion_db):
        """
        Test: Obtener solo promociones activas.
        
        Resultado esperado:
        - Retorna lista de promociones con estado ACTIVA
        """
        # Arrange
        with patch.object(self.service.repository, 'get_activas') as mock_get:
            mock_get.return_value = [mock_promocion_db]
            
            # Act
            resultado = self.service.get_activas()
            
            # Assert
            assert len(resultado) == 1
            mock_get.assert_called_once()

    # -------------------- GET SUGERIDAS --------------------

    def test_get_sugeridas_retorna_sugeridas(self, mock_promocion_db):
        """
        Test: Obtener promociones sugeridas.
        
        Resultado esperado:
        - Retorna lista de promociones con estado SUGERIDA
        """
        # Arrange
        mock_promocion_db.estado = EstadoPromocion.SUGERIDA
        
        with patch.object(self.service.repository, 'get_sugeridas') as mock_get:
            mock_get.return_value = [mock_promocion_db]
            
            # Act
            resultado = self.service.get_sugeridas()
            
            # Assert
            assert len(resultado) == 1
            mock_get.assert_called_once()

    # -------------------- CREATE --------------------

    def test_create_exitoso(self, mock_promocion_create, mock_promocion_db):
        """
        Test: Crear promoción exitosamente.
        
        Resultado esperado:
        - Retorna la promoción creada
        """
        # Arrange
        with patch.object(self.service.repository, 'get_next_codigo') as mock_codigo, \
             patch.object(self.service.repository, 'create') as mock_create:
            mock_codigo.return_value = "PROMO002"
            mock_create.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.create(mock_promocion_create)
            
            # Assert
            assert resultado is not None
            mock_create.assert_called_once()

    def test_create_genera_codigo_automatico(self, mock_promocion_db):
        """
        Test: Crear promoción sin código genera uno automáticamente.
        
        Resultado esperado:
        - Se genera un código automático
        """
        # Arrange
        promocion_sin_codigo = PromocionCreate(
            titulo="Sin Código",
            tipo_promocion=TipoPromocionEnum.DESCUENTO,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=7)
        )
        
        with patch.object(self.service.repository, 'get_next_codigo') as mock_codigo, \
             patch.object(self.service.repository, 'create') as mock_create:
            mock_codigo.return_value = "PROMO003"
            mock_create.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.create(promocion_sin_codigo)
            
            # Assert
            mock_codigo.assert_called_once()

    def test_create_con_codigo_proporcionado(self, mock_promocion_db):
        """
        Test: Crear promoción con código proporcionado.
        
        Resultado esperado:
        - Usa el código proporcionado
        """
        # Arrange
        promocion_con_codigo = PromocionCreate(
            codigo_promocion="MI_CODIGO",
            titulo="Con Código",
            tipo_promocion=TipoPromocionEnum.DESCUENTO,
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=7)
        )
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.create(promocion_con_codigo)
            
            # Assert
            call_args = mock_create.call_args[0][0]
            assert call_args['codigo_promocion'] == "MI_CODIGO"

    # -------------------- UPDATE --------------------

    def test_update_exitoso(self, mock_promocion_update, mock_promocion_db):
        """
        Test: Actualizar promoción existente.
        
        Resultado esperado:
        - Retorna la promoción actualizada
        """
        # Arrange
        mock_promocion_db.titulo = "Promoción Actualizada"
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.update(promocion_id=1, data=mock_promocion_update)
            
            # Assert
            assert resultado is not None
            assert resultado.titulo == "Promoción Actualizada"

    def test_update_no_encontrado(self, mock_promocion_update):
        """
        Test: Actualizar promoción que no existe.
        
        Resultado esperado:
        - Retorna None
        """
        # Arrange
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = None
            
            # Act
            resultado = self.service.update(promocion_id=999, data=mock_promocion_update)
            
            # Assert
            assert resultado is None

    # -------------------- CAMBIOS DE ESTADO --------------------

    def test_activar_promocion(self, mock_promocion_db):
        """
        Test: Activar una promoción sugerida.
        
        Resultado esperado:
        - Cambia estado a ACTIVA
        """
        # Arrange
        mock_promocion_db.estado = EstadoPromocion.ACTIVA
        
        with patch.object(self.service.repository, 'cambiar_estado') as mock_estado:
            mock_estado.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.activar(promocion_id=1)
            
            # Assert
            assert resultado is not None
            mock_estado.assert_called_once_with(1, EstadoPromocion.ACTIVA)

    def test_pausar_promocion(self, mock_promocion_db):
        """
        Test: Pausar una promoción activa.
        
        Resultado esperado:
        - Cambia estado a PAUSADA
        """
        # Arrange
        mock_promocion_db.estado = EstadoPromocion.PAUSADA
        
        with patch.object(self.service.repository, 'cambiar_estado') as mock_estado:
            mock_estado.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.pausar(promocion_id=1)
            
            # Assert
            mock_estado.assert_called_once_with(1, EstadoPromocion.PAUSADA)

    def test_cancelar_promocion(self, mock_promocion_db):
        """
        Test: Cancelar una promoción.
        
        Resultado esperado:
        - Cambia estado a CANCELADA
        """
        # Arrange
        mock_promocion_db.estado = EstadoPromocion.CANCELADA
        
        with patch.object(self.service.repository, 'cambiar_estado') as mock_estado:
            mock_estado.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.cancelar(promocion_id=1)
            
            # Assert
            mock_estado.assert_called_once_with(1, EstadoPromocion.CANCELADA)

    def test_finalizar_promocion(self, mock_promocion_db):
        """
        Test: Finalizar una promoción.
        
        Resultado esperado:
        - Cambia estado a FINALIZADA
        """
        # Arrange
        mock_promocion_db.estado = EstadoPromocion.FINALIZADA
        
        with patch.object(self.service.repository, 'cambiar_estado') as mock_estado:
            mock_estado.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.finalizar(promocion_id=1)
            
            # Assert
            mock_estado.assert_called_once_with(1, EstadoPromocion.FINALIZADA)

    # -------------------- DELETE --------------------

    def test_delete_exitoso(self):
        """
        Test: Eliminar (anular) promoción exitosamente.
        
        Resultado esperado:
        - Retorna True
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = True
            
            # Act
            resultado = self.service.delete(promocion_id=1)
            
            # Assert
            assert resultado is True
            mock_delete.assert_called_once_with(1)

    def test_delete_no_encontrado(self):
        """
        Test: Eliminar promoción que no existe.
        
        Resultado esperado:
        - Retorna False
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = False
            
            # Act
            resultado = self.service.delete(promocion_id=999)
            
            # Assert
            assert resultado is False

    # ==================== GENERAR SUGERENCIAS ====================

    def test_generar_sugerencias_con_productos_por_vencer(self, mock_producto_terminado):
        """
        Test: Generar sugerencias cuando hay productos por vencer.
        
        Resultado esperado:
        - Retorna lista de sugerencias ordenada por urgencia
        """
        # Arrange
        mock_producto_terminado.vida_util_dias = 7
        mock_producto_terminado.stock_actual = Decimal("20")
        mock_producto_terminado.precio_venta = Decimal("15")
        
        mock_movimiento = MagicMock()
        mock_movimiento.fecha_movimiento = datetime.now() - timedelta(days=5)
        
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [mock_producto_terminado]
        self.mock_db.query.return_value = mock_query
        
        # Simular que no hay movimientos
        mock_query.filter.return_value.order_by.return_value.first.return_value = None
        
        # Act
        resultado = self.service.generar_sugerencias(dias_alerta=7)
        
        # Assert
        assert isinstance(resultado, list)

    def test_generar_sugerencias_sin_productos_por_vencer(self):
        """
        Test: Generar sugerencias cuando no hay productos por vencer.
        
        Resultado esperado:
        - Retorna lista vacía
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        # Act
        resultado = self.service.generar_sugerencias(dias_alerta=7)
        
        # Assert
        assert resultado == []

    # ==================== CREAR DESDE SUGERENCIA ====================

    def test_crear_desde_sugerencia(self, mock_sugerencia, mock_promocion_db):
        """
        Test: Crear promoción activa desde sugerencia.
        
        Resultado esperado:
        - Crea promoción con estado ACTIVA
        """
        # Arrange
        with patch.object(self.service.repository, 'get_next_codigo') as mock_codigo, \
             patch.object(self.service.repository, 'create') as mock_create:
            mock_codigo.return_value = "PROMO-AUTO-001"
            mock_create.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.crear_desde_sugerencia(mock_sugerencia)
            
            # Assert
            assert resultado is not None
            call_args = mock_create.call_args[0][0]
            assert call_args['estado'] == EstadoPromocion.ACTIVA
            assert call_args['creado_automaticamente'] is True

    def test_crear_desde_sugerencia_con_fecha_fin_personalizada(self, mock_sugerencia, mock_promocion_db):
        """
        Test: Crear promoción desde sugerencia con fecha fin personalizada.
        
        Resultado esperado:
        - Usa la fecha fin proporcionada
        """
        # Arrange
        fecha_fin_custom = date.today() + timedelta(days=14)
        
        with patch.object(self.service.repository, 'get_next_codigo') as mock_codigo, \
             patch.object(self.service.repository, 'create') as mock_create:
            mock_codigo.return_value = "PROMO-AUTO-002"
            mock_create.return_value = mock_promocion_db
            
            # Act
            resultado = self.service.crear_desde_sugerencia(mock_sugerencia, fecha_fin=fecha_fin_custom)
            
            # Assert
            call_args = mock_create.call_args[0][0]
            assert call_args['fecha_fin'] == fecha_fin_custom

    # ==================== ESTADÍSTICAS ====================

    def test_get_estadisticas(self, mock_promocion_db):
        """
        Test: Obtener estadísticas de promociones.
        
        Resultado esperado:
        - Retorna objeto EstadisticasPromociones
        """
        # Arrange
        promo_activa = MagicMock()
        promo_activa.estado = EstadoPromocion.ACTIVA
        promo_activa.ahorro_potencial = Decimal("100")
        
        promo_sugerida = MagicMock()
        promo_sugerida.estado = EstadoPromocion.SUGERIDA
        promo_sugerida.ahorro_potencial = Decimal("50")
        
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []
        self.mock_db.query.return_value = mock_query
        
        with patch.object(self.service.repository, 'get_all') as mock_get_all, \
             patch.object(self.service, 'generar_sugerencias') as mock_sugerencias:
            mock_get_all.return_value = [promo_activa, promo_sugerida]
            mock_sugerencias.return_value = []
            
            # Act
            resultado = self.service.get_estadisticas()
            
            # Assert
            assert resultado.total_promociones == 2
            assert resultado.promociones_activas == 1
            assert resultado.promociones_sugeridas == 1

    # -------------------- HELPERS INTERNOS --------------------

    def test_generar_titulo_liquidacion(self):
        """
        Test: Generar título para promoción de liquidación.
        
        Resultado esperado:
        - Título contiene "LIQUIDACIÓN"
        """
        # Act
        titulo = self.service._generar_titulo("Pan Integral", TipoPromocion.LIQUIDACION, 1)
        
        # Assert
        assert "LIQUIDACIÓN" in titulo

    def test_generar_titulo_oferta_urgente(self):
        """
        Test: Generar título para producto con pocos días.
        
        Resultado esperado:
        - Título contiene "Oferta Especial"
        """
        # Act
        titulo = self.service._generar_titulo("Pan Integral", TipoPromocion.DESCUENTO, 2)
        
        # Assert
        assert "Oferta Especial" in titulo

    def test_generar_descripcion_liquidacion(self):
        """
        Test: Generar descripción para liquidación.
        
        Resultado esperado:
        - Descripción menciona liquidación
        """
        # Act
        descripcion = self.service._generar_descripcion("Pan", TipoPromocion.LIQUIDACION, 1, 50)
        
        # Assert
        assert "liquidación" in descripcion.lower()

    def test_generar_descripcion_descuento(self):
        """
        Test: Generar descripción para descuento normal.
        
        Resultado esperado:
        - Descripción incluye el porcentaje de descuento
        """
        # Act
        descripcion = self.service._generar_descripcion("Pan", TipoPromocion.DESCUENTO, 5, 20)
        
        # Assert
        assert "20%" in descripcion
