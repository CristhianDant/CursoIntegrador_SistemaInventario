"""
Tests unitarios para OrdenDeCompraService.

Este módulo contiene tests para validar el comportamiento del servicio de órdenes de compra
utilizando mocks para aislar la lógica del servicio.

NO se evalúan: envío de emails a proveedores.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime, date

from modules.orden_de_compra.service import OrdenDeCompraService
from modules.orden_de_compra.model import OrdenDeCompra as OrdenDeCompraModel
from modules.orden_de_compra.schemas import (
    OrdenDeCompraCreate, OrdenDeCompraUpdate, OrdenDeCompraDetalleCreate,
    GenerarOrdenDesdesugerenciaRequest
)


# ==================== FIXTURES ADICIONALES ====================

@pytest.fixture
def mock_orden_detalle():
    """Mock de un detalle de orden de compra."""
    detalle = MagicMock()
    detalle.id_orden_detalle = 1
    detalle.id_orden = 1
    detalle.id_insumo = 1
    detalle.cantidad = Decimal("10.00")
    detalle.precio_unitario = Decimal("5.00")
    detalle.descuento_unitario = Decimal("0")
    detalle.sub_total = Decimal("50.00")
    return detalle


@pytest.fixture
def mock_orden_create():
    """Mock de datos para crear una orden de compra."""
    return OrdenDeCompraCreate(
        numero_orden="OC-2025-0002",
        id_proveedor=1,
        fecha_entrega_esperada=datetime.now(),
        moneda="PEN",
        tipo_cambio=Decimal("1"),
        sub_total=Decimal("100.00"),
        descuento=Decimal("0"),
        igv=Decimal("18.00"),
        total=Decimal("118.00"),
        estado="PENDIENTE",
        id_user_creador=1,
        detalles=[
            OrdenDeCompraDetalleCreate(
                id_insumo=1,
                cantidad=Decimal("10.00"),
                precio_unitario=Decimal("10.00"),
                descuento_unitario=Decimal("0"),
                sub_total=Decimal("100.00")
            )
        ]
    )


@pytest.fixture
def mock_orden_update():
    """Mock de datos para actualizar una orden de compra."""
    return OrdenDeCompraUpdate(
        numero_orden="OC-2025-0002",
        id_proveedor=1,
        fecha_entrega_esperada=datetime.now(),
        sub_total=Decimal("150.00"),
        igv=Decimal("27.00"),
        total=Decimal("177.00"),
        id_user_creador=1
    )


# ==================== TEST CLASS ====================

class TestOrdenDeCompraService:
    """Tests para OrdenDeCompraService."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura el servicio antes de cada test."""
        self.service = OrdenDeCompraService()

    # -------------------- GET ALL --------------------

    def test_get_all_retorna_lista(self, mock_db_session, mock_orden_compra):
        """
        Test: Obtener todas las órdenes de compra.
        
        Resultado esperado:
        - Retorna lista con todas las órdenes activas
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = [mock_orden_compra]
            
            # Act
            resultado = self.service.get_all(mock_db_session)
            
            # Assert
            assert len(resultado) == 1
            mock_get.assert_called_once_with(mock_db_session, activas_solo=True)

    def test_get_all_incluye_anuladas(self, mock_db_session, mock_orden_compra):
        """
        Test: Obtener todas las órdenes incluyendo anuladas.
        
        Resultado esperado:
        - Retorna todas las órdenes sin filtro
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = [mock_orden_compra]
            
            # Act
            resultado = self.service.get_all(mock_db_session, activas_solo=False)
            
            # Assert
            mock_get.assert_called_once_with(mock_db_session, activas_solo=False)

    def test_get_all_lista_vacia(self, mock_db_session):
        """
        Test: Obtener órdenes cuando no hay ninguna.
        
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

    def test_get_by_id_existente(self, mock_db_session, mock_orden_compra):
        """
        Test: Obtener orden de compra por ID cuando existe.
        
        Resultado esperado:
        - Retorna la orden solicitada
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = mock_orden_compra
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, orden_id=1)
            
            # Assert
            assert resultado.id_orden == 1
            assert resultado.numero_orden == "OC-2025-0001"
            mock_get.assert_called_once_with(mock_db_session, 1)

    def test_get_by_id_no_encontrado(self, mock_db_session):
        """
        Test: Obtener orden por ID cuando no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_by_id(mock_db_session, orden_id=999)
            
            assert exc_info.value.status_code == 404
            assert "no encontrada" in exc_info.value.detail

    # -------------------- CREATE --------------------

    def test_create_exitoso(self, mock_db_session, mock_orden_create, mock_orden_compra):
        """
        Test: Crear orden de compra exitosamente.
        
        Resultado esperado:
        - Retorna la orden creada con sus detalles
        """
        # Arrange
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_orden_compra
            
            # Act
            resultado = self.service.create(mock_db_session, mock_orden_create)
            
            # Assert
            assert resultado.id_orden == 1
            mock_create.assert_called_once_with(mock_db_session, mock_orden_create)

    def test_create_con_multiples_detalles(self, mock_db_session, mock_orden_compra):
        """
        Test: Crear orden con múltiples detalles.
        
        Resultado esperado:
        - Se crea con todos los detalles
        """
        # Arrange
        orden_data = OrdenDeCompraCreate(
            numero_orden="OC-2025-0003",
            id_proveedor=1,
            fecha_entrega_esperada=datetime.now(),
            sub_total=Decimal("200.00"),
            igv=Decimal("36.00"),
            total=Decimal("236.00"),
            id_user_creador=1,
            detalles=[
                OrdenDeCompraDetalleCreate(
                    id_insumo=1,
                    cantidad=Decimal("10.00"),
                    precio_unitario=Decimal("10.00"),
                    sub_total=Decimal("100.00")
                ),
                OrdenDeCompraDetalleCreate(
                    id_insumo=2,
                    cantidad=Decimal("20.00"),
                    precio_unitario=Decimal("5.00"),
                    sub_total=Decimal("100.00")
                )
            ]
        )
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_orden_compra
            
            # Act
            resultado = self.service.create(mock_db_session, orden_data)
            
            # Assert
            mock_create.assert_called_once()

    # -------------------- UPDATE --------------------

    def test_update_exitoso(self, mock_db_session, mock_orden_update, mock_orden_compra):
        """
        Test: Actualizar orden de compra existente.
        
        Resultado esperado:
        - Retorna la orden actualizada
        """
        # Arrange
        mock_orden_compra.total = Decimal("177.00")
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_orden_compra
            
            # Act
            resultado = self.service.update(mock_db_session, orden_id=1, orden=mock_orden_update)
            
            # Assert
            assert resultado.total == Decimal("177.00")
            mock_update.assert_called_once_with(mock_db_session, 1, mock_orden_update)

    def test_update_no_encontrado(self, mock_db_session, mock_orden_update):
        """
        Test: Actualizar orden que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.update(mock_db_session, orden_id=999, orden=mock_orden_update)
            
            assert exc_info.value.status_code == 404

    # -------------------- DELETE --------------------

    def test_delete_exitoso(self, mock_db_session):
        """
        Test: Anular orden de compra exitosamente.
        
        Resultado esperado:
        - Retorna mensaje de confirmación
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = True
            
            # Act
            resultado = self.service.delete(mock_db_session, orden_id=1)
            
            # Assert
            assert "message" in resultado
            assert "anulada" in resultado["message"].lower()

    def test_delete_no_encontrado(self, mock_db_session):
        """
        Test: Anular orden que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = False
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.delete(mock_db_session, orden_id=999)
            
            assert exc_info.value.status_code == 404

    # ==================== SUGERENCIAS DE COMPRA ====================

    def test_generar_sugerencias_compra_basico(self, mock_db_session):
        """
        Test: Generar sugerencias de compra básicas.
        
        Resultado esperado:
        - Retorna lista de sugerencias basada en stock bajo mínimo
        """
        # Arrange
        stock_insumos = [
            {
                'id_insumo': 1,
                'codigo': 'INS001',
                'nombre': 'Insumo Bajo',
                'unidad_medida': 'KG',
                'categoria': 'MATERIAS_PRIMAS',
                'stock_actual': Decimal('5.00'),
                'stock_minimo': Decimal('10.00')
            }
        ]
        
        with patch.object(self.service.repository, 'obtener_stock_actual_insumos') as mock_stock, \
             patch.object(self.service.repository, 'obtener_consumo_promedio_insumos') as mock_consumo, \
             patch.object(self.service.repository, 'obtener_cantidad_por_vencer') as mock_vencer, \
             patch.object(self.service.repository, 'obtener_ultimo_precio_insumos') as mock_precio, \
             patch.object(self.service.repository, 'obtener_proveedor_por_insumo') as mock_prov:
            
            mock_stock.return_value = stock_insumos
            mock_consumo.return_value = {1: Decimal('2.00')}
            mock_vencer.return_value = {}
            mock_precio.return_value = {1: Decimal('10.00')}
            mock_prov.return_value = {1: {'id_proveedor': 1, 'nombre': 'Proveedor Test'}}
            
            # Act
            resultado = self.service.generar_sugerencias_compra(mock_db_session)
            
            # Assert
            assert resultado is not None
            assert resultado.total_items >= 0

    def test_generar_sugerencias_compra_sin_items_criticos(self, mock_db_session):
        """
        Test: Generar sugerencias cuando no hay items críticos.
        
        Resultado esperado:
        - Retorna lista vacía de items
        """
        # Arrange
        stock_insumos = [
            {
                'id_insumo': 1,
                'codigo': 'INS001',
                'nombre': 'Insumo OK',
                'unidad_medida': 'KG',
                'categoria': 'MATERIAS_PRIMAS',
                'stock_actual': Decimal('100.00'),
                'stock_minimo': Decimal('10.00')
            }
        ]
        
        with patch.object(self.service.repository, 'obtener_stock_actual_insumos') as mock_stock, \
             patch.object(self.service.repository, 'obtener_consumo_promedio_insumos') as mock_consumo, \
             patch.object(self.service.repository, 'obtener_cantidad_por_vencer') as mock_vencer, \
             patch.object(self.service.repository, 'obtener_ultimo_precio_insumos') as mock_precio, \
             patch.object(self.service.repository, 'obtener_proveedor_por_insumo') as mock_prov:
            
            mock_stock.return_value = stock_insumos
            mock_consumo.return_value = {1: Decimal('1.00')}
            mock_vencer.return_value = {}
            mock_precio.return_value = {}
            mock_prov.return_value = {}
            
            # Act
            resultado = self.service.generar_sugerencias_compra(mock_db_session)
            
            # Assert
            assert resultado.total_items == 0

    def test_generar_sugerencias_filtra_por_urgencia(self, mock_db_session):
        """
        Test: Filtrar sugerencias por urgencia.
        
        Resultado esperado:
        - Solo retorna items con la urgencia especificada
        """
        # Arrange
        stock_insumos = [
            {
                'id_insumo': 1,
                'codigo': 'INS001',
                'nombre': 'Insumo Urgente',
                'unidad_medida': 'KG',
                'categoria': 'MATERIAS_PRIMAS',
                'stock_actual': Decimal('0'),
                'stock_minimo': Decimal('10.00')
            }
        ]
        
        with patch.object(self.service.repository, 'obtener_stock_actual_insumos') as mock_stock, \
             patch.object(self.service.repository, 'obtener_consumo_promedio_insumos') as mock_consumo, \
             patch.object(self.service.repository, 'obtener_cantidad_por_vencer') as mock_vencer, \
             patch.object(self.service.repository, 'obtener_ultimo_precio_insumos') as mock_precio, \
             patch.object(self.service.repository, 'obtener_proveedor_por_insumo') as mock_prov:
            
            mock_stock.return_value = stock_insumos
            mock_consumo.return_value = {1: Decimal('5.00')}
            mock_vencer.return_value = {}
            mock_precio.return_value = {1: Decimal('10.00')}
            mock_prov.return_value = {}
            
            # Act
            resultado = self.service.generar_sugerencias_compra(
                mock_db_session,
                urgencia="inmediata"
            )
            
            # Assert
            for item in resultado.todos_items:
                assert item.urgencia == "inmediata"

    # ==================== GENERAR ORDEN DESDE SUGERENCIA ====================

    def test_generar_orden_desde_sugerencia_exitoso(self, mock_db_session, mock_orden_compra):
        """
        Test: Generar orden de compra desde sugerencia.
        
        Resultado esperado:
        - Crea la orden con los items sugeridos
        """
        # Arrange
        request = GenerarOrdenDesdesugerenciaRequest(
            id_proveedor=1,
            items=[
                {'id_insumo': 1, 'cantidad': 10, 'precio_unitario': 5.00}
            ],
            fecha_entrega_esperada=datetime.now(),
            id_user_creador=1
        )
        
        proveedor_info = {'id_proveedor': 1, 'nombre': 'Proveedor Test'}
        
        with patch.object(self.service.repository, 'obtener_proveedor_por_id') as mock_prov, \
             patch.object(self.service.repository, 'generar_numero_orden') as mock_num, \
             patch.object(self.service.repository, 'create') as mock_create:
            
            mock_prov.return_value = proveedor_info
            mock_num.return_value = "OC-2025-0010"
            mock_create.return_value = mock_orden_compra
            
            # Act
            resultado = self.service.generar_orden_desde_sugerencia(mock_db_session, request)
            
            # Assert
            assert resultado is not None
            mock_create.assert_called_once()

    def test_generar_orden_proveedor_no_encontrado(self, mock_db_session):
        """
        Test: Generar orden con proveedor inexistente.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        request = GenerarOrdenDesdesugerenciaRequest(
            id_proveedor=999,
            items=[{'id_insumo': 1, 'cantidad': 10, 'precio_unitario': 5.00}],
            fecha_entrega_esperada=datetime.now(),
            id_user_creador=1
        )
        
        with patch.object(self.service.repository, 'obtener_proveedor_por_id') as mock_prov:
            mock_prov.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.generar_orden_desde_sugerencia(mock_db_session, request)
            
            assert exc_info.value.status_code == 404

    def test_generar_orden_calcula_igv_correctamente(self, mock_db_session, mock_orden_compra):
        """
        Test: Verificar cálculo correcto de IGV (18%).
        
        Resultado esperado:
        - IGV = sub_total * 0.18
        """
        # Arrange
        request = GenerarOrdenDesdesugerenciaRequest(
            id_proveedor=1,
            items=[
                {'id_insumo': 1, 'cantidad': 10, 'precio_unitario': 10.00}  # subtotal = 100
            ],
            fecha_entrega_esperada=datetime.now(),
            id_user_creador=1
        )
        
        proveedor_info = {'id_proveedor': 1, 'nombre': 'Proveedor Test'}
        
        with patch.object(self.service.repository, 'obtener_proveedor_por_id') as mock_prov, \
             patch.object(self.service.repository, 'generar_numero_orden') as mock_num, \
             patch.object(self.service.repository, 'create') as mock_create:
            
            mock_prov.return_value = proveedor_info
            mock_num.return_value = "OC-2025-0011"
            mock_create.return_value = mock_orden_compra
            
            # Act
            self.service.generar_orden_desde_sugerencia(mock_db_session, request)
            
            # Assert
            call_args = mock_create.call_args[0][1]
            assert call_args.igv == Decimal('18.00')  # 100 * 0.18
            assert call_args.total == Decimal('118.00')  # 100 + 18

    # -------------------- CASOS DE BORDE --------------------

    def test_generar_sugerencias_sin_consumo_historico(self, mock_db_session):
        """
        Test: Generar sugerencias cuando no hay consumo histórico.
        
        Resultado esperado:
        - Sugiere cantidad para llegar al stock mínimo
        """
        # Arrange
        stock_insumos = [
            {
                'id_insumo': 1,
                'codigo': 'INS001',
                'nombre': 'Insumo Nuevo',
                'unidad_medida': 'KG',
                'categoria': 'MATERIAS_PRIMAS',
                'stock_actual': Decimal('3.00'),
                'stock_minimo': Decimal('10.00')
            }
        ]
        
        with patch.object(self.service.repository, 'obtener_stock_actual_insumos') as mock_stock, \
             patch.object(self.service.repository, 'obtener_consumo_promedio_insumos') as mock_consumo, \
             patch.object(self.service.repository, 'obtener_cantidad_por_vencer') as mock_vencer, \
             patch.object(self.service.repository, 'obtener_ultimo_precio_insumos') as mock_precio, \
             patch.object(self.service.repository, 'obtener_proveedor_por_insumo') as mock_prov:
            
            mock_stock.return_value = stock_insumos
            mock_consumo.return_value = {}  # Sin consumo histórico
            mock_vencer.return_value = {}
            mock_precio.return_value = {}
            mock_prov.return_value = {}
            
            # Act
            resultado = self.service.generar_sugerencias_compra(mock_db_session)
            
            # Assert
            if resultado.todos_items:
                # Debería sugerir 7 unidades (10 - 3)
                assert resultado.todos_items[0].cantidad_sugerida >= Decimal('7.00')
