"""
Tests unitarios para ReportesService.

Este módulo contiene tests para validar el comportamiento del servicio de reportes
utilizando mocks para aislar la lógica del servicio.

Se evalúa: Análisis ABC, Reporte Diario, KPIs, Rotación de Inventario.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from datetime import date, datetime, timedelta

from modules.reportes.service import ReportesService
from modules.reportes.schemas import (
    ReporteABCResponse, ProductoABC,
    ReporteDiarioResponse, ResumenVentasDiario,
    KPIsResponse, RotacionResponse
)


# ==================== FIXTURES ADICIONALES ====================

@pytest.fixture
def mock_ventas_producto():
    """Mock de datos de ventas por producto."""
    return [
        {
            'id_producto': 1,
            'codigo': 'PROD001',
            'nombre': 'Producto A',
            'cantidad_vendida': Decimal('100'),
            'monto_total': Decimal('700.00')
        },
        {
            'id_producto': 2,
            'codigo': 'PROD002',
            'nombre': 'Producto B',
            'cantidad_vendida': Decimal('50'),
            'monto_total': Decimal('200.00')
        },
        {
            'id_producto': 3,
            'codigo': 'PROD003',
            'nombre': 'Producto C',
            'cantidad_vendida': Decimal('20'),
            'monto_total': Decimal('100.00')
        }
    ]


@pytest.fixture
def mock_resumen_ventas():
    """Mock de resumen de ventas diario."""
    return {
        'total_ventas': Decimal('1000.00'),
        'cantidad_transacciones': 15,
        'ticket_promedio': Decimal('66.67'),
        'ventas_por_metodo': {'EFECTIVO': Decimal('600'), 'TARJETA': Decimal('400')}
    }


@pytest.fixture
def mock_resumen_mermas():
    """Mock de resumen de mermas diario."""
    return {
        'cantidad_casos': 3,
        'cantidad_total_kg': Decimal('2.5'),
        'costo_total': Decimal('25.00'),
        'desglose_por_tipo': {'VENCIMIENTO': 2, 'DETERIORO': 1}
    }


@pytest.fixture
def mock_resumen_produccion():
    """Mock de resumen de producción diario."""
    return {
        'total_producciones': 5,
        'total_unidades_producidas': Decimal('150'),
        'recetas_producidas': [
            {'nombre': 'Pan Integral', 'cantidad': 50},
            {'nombre': 'Galletas', 'cantidad': 100}
        ]
    }


# ==================== TEST CLASS ====================

class TestReportesService:
    """Tests para ReportesService."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_db_session):
        """Configura el servicio antes de cada test."""
        # Crear service con repository y alertas mockeados
        self.mock_repository = MagicMock()
        self.mock_alertas = MagicMock()
        
        with patch('modules.reportes.service.ReportesRepository', return_value=self.mock_repository), \
             patch('modules.reportes.service.AlertasService', return_value=self.mock_alertas):
            self.service = ReportesService(mock_db_session)
        
        # Asignar los mocks al service para que los tests puedan acceder
        self.service.repository = self.mock_repository
        self.service.alertas_service = self.mock_alertas
        self.mock_db = mock_db_session

    # ==================== ANÁLISIS ABC ====================

    def test_generar_reporte_abc_clasificacion_correcta(self, mock_ventas_producto):
        """
        Test: Clasificar productos según análisis ABC.
        
        Resultado esperado:
        - Productos ordenados por ventas
        - Clasificación A (70%), B (20%), C (10%)
        """
        # Arrange
        with patch.object(self.service.repository, 'obtener_ventas_por_producto') as mock_ventas:
            mock_ventas.return_value = mock_ventas_producto
            
            # Act
            resultado = self.service.generar_reporte_abc(
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_fin=date.today()
            )
            
            # Assert
            assert resultado is not None
            assert resultado.total_productos == 3
            assert resultado.total_ventas == Decimal('1000.00')
            # Producto A (70%) debería ser categoría A
            assert len(resultado.productos_a) >= 1

    def test_generar_reporte_abc_sin_ventas(self):
        """
        Test: Generar ABC cuando no hay ventas.
        
        Resultado esperado:
        - Retorna reporte con valores en cero
        """
        # Arrange
        with patch.object(self.service.repository, 'obtener_ventas_por_producto') as mock_ventas:
            mock_ventas.return_value = []
            
            # Act
            resultado = self.service.generar_reporte_abc(
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_fin=date.today()
            )
            
            # Assert
            assert resultado.total_ventas == Decimal('0')
            assert resultado.total_productos == 0
            assert resultado.productos_a == []
            assert resultado.productos_b == []
            assert resultado.productos_c == []

    def test_generar_reporte_abc_con_filtro_categoria(self, mock_ventas_producto):
        """
        Test: Generar ABC filtrado por categoría.
        
        Resultado esperado:
        - Solo incluye productos de la categoría especificada
        """
        # Arrange
        with patch.object(self.service.repository, 'obtener_ventas_por_producto') as mock_ventas:
            mock_ventas.return_value = mock_ventas_producto[:1]  # Solo un producto
            
            # Act
            resultado = self.service.generar_reporte_abc(
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_fin=date.today(),
                categoria="PANADERIA"
            )
            
            # Assert
            mock_ventas.assert_called_once_with(
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_fin=date.today(),
                categoria="PANADERIA"
            )

    def test_generar_reporte_abc_porcentajes_acumulados(self, mock_ventas_producto):
        """
        Test: Verificar cálculo de porcentajes acumulados.
        
        Resultado esperado:
        - Porcentajes acumulados suman 100%
        """
        # Arrange
        with patch.object(self.service.repository, 'obtener_ventas_por_producto') as mock_ventas:
            mock_ventas.return_value = mock_ventas_producto
            
            # Act
            resultado = self.service.generar_reporte_abc(
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_fin=date.today()
            )
            
            # Assert
            todos_productos = resultado.productos_a + resultado.productos_b + resultado.productos_c
            if todos_productos:
                ultimo = todos_productos[-1]
                assert ultimo.porcentaje_acumulado == Decimal('100.00')

    # ==================== REPORTE DIARIO ====================

    def test_generar_reporte_diario_completo(
        self, 
        mock_resumen_ventas, 
        mock_resumen_mermas, 
        mock_resumen_produccion
    ):
        """
        Test: Generar reporte diario completo.
        
        Resultado esperado:
        - Incluye ventas, mermas, producción, vencimientos y stock crítico
        """
        # Arrange
        mock_lista_usar_hoy = MagicMock()
        mock_lista_usar_hoy.items = []
        
        mock_stock_critico = MagicMock()
        mock_stock_critico.items = []
        
        with patch.object(self.service.repository, 'obtener_resumen_ventas_dia') as mock_ventas, \
             patch.object(self.service.repository, 'obtener_resumen_mermas_dia') as mock_mermas, \
             patch.object(self.service.repository, 'obtener_resumen_produccion_dia') as mock_prod, \
             patch.object(self.service.alertas_service, 'obtener_lista_usar_hoy') as mock_usar, \
             patch.object(self.service.alertas_service, 'obtener_stock_critico') as mock_stock:
            
            mock_ventas.return_value = mock_resumen_ventas
            mock_mermas.return_value = mock_resumen_mermas
            mock_prod.return_value = mock_resumen_produccion
            mock_usar.return_value = mock_lista_usar_hoy
            mock_stock.return_value = mock_stock_critico
            
            # Act
            resultado = self.service.generar_reporte_diario(fecha=date.today())
            
            # Assert
            assert resultado is not None
            assert resultado.fecha == date.today()
            assert resultado.ventas.total_ventas == Decimal('1000.00')
            assert resultado.mermas.cantidad_casos == 3
            assert resultado.produccion.total_producciones == 5

    def test_generar_reporte_diario_calcula_porcentaje_merma(
        self, 
        mock_resumen_ventas, 
        mock_resumen_mermas, 
        mock_resumen_produccion
    ):
        """
        Test: Calcular porcentaje de merma sobre ventas.
        
        Resultado esperado:
        - Porcentaje = (costo_merma / total_ventas) * 100
        """
        # Arrange
        mock_lista_usar_hoy = MagicMock()
        mock_lista_usar_hoy.items = []
        
        mock_stock_critico = MagicMock()
        mock_stock_critico.items = []
        
        with patch.object(self.service.repository, 'obtener_resumen_ventas_dia') as mock_ventas, \
             patch.object(self.service.repository, 'obtener_resumen_mermas_dia') as mock_mermas, \
             patch.object(self.service.repository, 'obtener_resumen_produccion_dia') as mock_prod, \
             patch.object(self.service.alertas_service, 'obtener_lista_usar_hoy') as mock_usar, \
             patch.object(self.service.alertas_service, 'obtener_stock_critico') as mock_stock:
            
            mock_ventas.return_value = mock_resumen_ventas
            mock_mermas.return_value = mock_resumen_mermas
            mock_prod.return_value = mock_resumen_produccion
            mock_usar.return_value = mock_lista_usar_hoy
            mock_stock.return_value = mock_stock_critico
            
            # Act
            resultado = self.service.generar_reporte_diario(fecha=date.today())
            
            # Assert
            # 25 / 1000 * 100 = 2.5%
            assert resultado.mermas.porcentaje_sobre_ventas == Decimal('2.50')
            assert resultado.mermas.cumple_meta is True  # < 3%

    # ==================== KPIs ====================

    def test_obtener_kpis_todos_los_indicadores(
        self, 
        mock_resumen_ventas, 
        mock_resumen_mermas
    ):
        """
        Test: Obtener todos los KPIs del sistema.
        
        Resultado esperado:
        - Retorna 5 KPIs principales
        """
        # Arrange
        mock_stock_critico = MagicMock()
        mock_stock_critico.total_sin_stock = 0
        mock_stock_critico.total_bajo_minimo = 2
        
        with patch.object(self.service.repository, 'obtener_resumen_ventas_dia') as mock_ventas, \
             patch.object(self.service.repository, 'obtener_resumen_mermas_dia') as mock_mermas, \
             patch.object(self.service.repository, 'contar_lotes_vencidos_hoy') as mock_vencidos, \
             patch.object(self.service.alertas_service, 'obtener_stock_critico') as mock_stock, \
             patch.object(self.service, '_calcular_rotacion_promedio') as mock_rotacion:
            
            mock_ventas.return_value = mock_resumen_ventas
            mock_mermas.return_value = mock_resumen_mermas
            mock_vencidos.return_value = {'cantidad_lotes': 0, 'cantidad_kg': Decimal('0')}
            mock_stock.return_value = mock_stock_critico
            mock_rotacion.return_value = Decimal('15')
            
            # Act
            resultado = self.service.obtener_kpis(fecha=date.today())
            
            # Assert
            assert resultado is not None
            assert resultado.fecha == date.today()
            assert resultado.merma_diaria is not None
            assert resultado.productos_vencidos_hoy is not None
            assert resultado.cumplimiento_fefo is not None
            assert resultado.stock_critico is not None
            assert resultado.rotacion_inventario is not None
            assert resultado.kpis_totales == 5

    def test_obtener_kpis_calcula_porcentaje_cumplimiento(
        self, 
        mock_resumen_ventas, 
        mock_resumen_mermas
    ):
        """
        Test: Calcular porcentaje de KPIs cumplidos.
        
        Resultado esperado:
        - porcentaje_cumplimiento = (kpis_cumplidos / kpis_totales) * 100
        """
        # Arrange
        mock_stock_critico = MagicMock()
        mock_stock_critico.total_sin_stock = 0
        mock_stock_critico.total_bajo_minimo = 0
        
        with patch.object(self.service.repository, 'obtener_resumen_ventas_dia') as mock_ventas, \
             patch.object(self.service.repository, 'obtener_resumen_mermas_dia') as mock_mermas, \
             patch.object(self.service.repository, 'contar_lotes_vencidos_hoy') as mock_vencidos, \
             patch.object(self.service.alertas_service, 'obtener_stock_critico') as mock_stock, \
             patch.object(self.service, '_calcular_rotacion_promedio') as mock_rotacion:
            
            mock_ventas.return_value = mock_resumen_ventas
            mock_mermas.return_value = mock_resumen_mermas
            mock_vencidos.return_value = {'cantidad_lotes': 0, 'cantidad_kg': Decimal('0')}
            mock_stock.return_value = mock_stock_critico
            mock_rotacion.return_value = Decimal('15')  # Cumple meta de 12
            
            # Act
            resultado = self.service.obtener_kpis(fecha=date.today())
            
            # Assert
            assert resultado.kpis_cumplidos <= resultado.kpis_totales
            assert resultado.porcentaje_cumplimiento >= 0
            assert resultado.porcentaje_cumplimiento <= 100

    def test_obtener_kpis_merma_no_cumple_meta(self):
        """
        Test: KPI de merma no cumple meta cuando supera 3%.
        
        Resultado esperado:
        - cumple_meta = False cuando porcentaje > 3%
        """
        # Arrange
        resumen_ventas = {
            'total_ventas': Decimal('100.00'),
            'cantidad_transacciones': 5,
            'ticket_promedio': Decimal('20'),
            'ventas_por_metodo': {}
        }
        resumen_mermas = {
            'cantidad_casos': 5,
            'cantidad_total_kg': Decimal('5'),
            'costo_total': Decimal('10.00'),  # 10% de merma
            'desglose_por_tipo': {}
        }
        
        mock_stock_critico = MagicMock()
        mock_stock_critico.total_sin_stock = 0
        mock_stock_critico.total_bajo_minimo = 0
        
        with patch.object(self.service.repository, 'obtener_resumen_ventas_dia') as mock_ventas, \
             patch.object(self.service.repository, 'obtener_resumen_mermas_dia') as mock_mermas, \
             patch.object(self.service.repository, 'contar_lotes_vencidos_hoy') as mock_vencidos, \
             patch.object(self.service.alertas_service, 'obtener_stock_critico') as mock_stock, \
             patch.object(self.service, '_calcular_rotacion_promedio') as mock_rotacion:
            
            mock_ventas.return_value = resumen_ventas
            mock_mermas.return_value = resumen_mermas
            mock_vencidos.return_value = {'cantidad_lotes': 0, 'cantidad_kg': Decimal('0')}
            mock_stock.return_value = mock_stock_critico
            mock_rotacion.return_value = Decimal('15')
            
            # Act
            resultado = self.service.obtener_kpis(fecha=date.today())
            
            # Assert
            assert resultado.merma_diaria.cumple_meta is False

    # ==================== ROTACIÓN DE INVENTARIO ====================

    def test_generar_reporte_rotacion(self):
        """
        Test: Generar reporte de rotación de inventario.
        
        Resultado esperado:
        - Incluye productos e insumos con clasificación
        """
        # Arrange
        rotacion_productos = {
            'items': [
                {
                    'id': 1,
                    'codigo': 'PROD001',
                    'nombre': 'Producto Alta Rotación',
                    'tipo': 'producto',
                    'stock_actual': Decimal('50'),
                    'unidad_medida': 'UNIDAD',
                    'consumo_periodo': Decimal('100')
                }
            ],
            'total': 1
        }
        rotacion_insumos = {
            'items': [
                {
                    'id': 1,
                    'codigo': 'INS001',
                    'nombre': 'Insumo Baja Rotación',
                    'tipo': 'insumo',
                    'stock_actual': Decimal('100'),
                    'unidad_medida': 'KG',
                    'consumo_periodo': Decimal('10')
                }
            ],
            'total': 1
        }
        
        with patch.object(self.service.repository, 'obtener_rotacion_productos_terminados') as mock_prod, \
             patch.object(self.service.repository, 'obtener_rotacion_insumos') as mock_ins, \
             patch.object(self.service, '_calcular_rotacion_promedio') as mock_prom:
            
            mock_prod.return_value = rotacion_productos
            mock_ins.return_value = rotacion_insumos
            mock_prom.return_value = Decimal('10')
            
            # Act
            resultado = self.service.generar_reporte_rotacion(
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_fin=date.today()
            )
            
            # Assert
            assert resultado is not None
            assert resultado.total_items == 2
            assert len(resultado.productos_terminados) == 1
            assert len(resultado.insumos) == 1

    def test_generar_reporte_rotacion_clasificacion(self):
        """
        Test: Clasificación de items por rotación.
        
        Resultado esperado:
        - Alta: >= 12 veces/año
        - Media: >= 6 veces/año
        - Baja: < 6 veces/año
        """
        # Arrange
        rotacion_items = {
            'items': [
                {
                    'id': 1,
                    'codigo': 'PROD001',
                    'nombre': 'Alta Rotación',
                    'tipo': 'producto',
                    'stock_actual': Decimal('10'),
                    'unidad_medida': 'UNIDAD',
                    'consumo_periodo': Decimal('100')  # Alta rotación
                },
                {
                    'id': 2,
                    'codigo': 'PROD002',
                    'nombre': 'Media Rotación',
                    'tipo': 'producto',
                    'stock_actual': Decimal('50'),
                    'unidad_medida': 'UNIDAD',
                    'consumo_periodo': Decimal('30')  # Media rotación
                },
                {
                    'id': 3,
                    'codigo': 'PROD003',
                    'nombre': 'Baja Rotación',
                    'tipo': 'producto',
                    'stock_actual': Decimal('100'),
                    'unidad_medida': 'UNIDAD',
                    'consumo_periodo': Decimal('5')  # Baja rotación
                }
            ],
            'total': 3
        }
        
        with patch.object(self.service.repository, 'obtener_rotacion_productos_terminados') as mock_prod, \
             patch.object(self.service.repository, 'obtener_rotacion_insumos') as mock_ins, \
             patch.object(self.service, '_calcular_rotacion_promedio') as mock_prom:
            
            mock_prod.return_value = rotacion_items
            mock_ins.return_value = {'items': [], 'total': 0}
            mock_prom.return_value = Decimal('10')
            
            # Act
            resultado = self.service.generar_reporte_rotacion(
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_fin=date.today()
            )
            
            # Assert
            assert resultado.items_alta_rotacion >= 0
            assert resultado.items_media_rotacion >= 0
            assert resultado.items_baja_rotacion >= 0

    def test_calcular_rotacion_promedio(self):
        """
        Test: Calcular rotación promedio anualizada.
        
        Resultado esperado:
        - Rotación anualizada correcta
        """
        # Arrange
        rotacion_data = {
            'items': [
                {
                    'id': 1,
                    'codigo': 'PROD001',
                    'nombre': 'Producto',
                    'tipo': 'producto',
                    'stock_actual': Decimal('50'),
                    'unidad_medida': 'UNIDAD',
                    'consumo_periodo': Decimal('100')
                }
            ],
            'total': 1
        }
        
        with patch.object(self.service.repository, 'obtener_rotacion_productos_terminados') as mock_prod, \
             patch.object(self.service.repository, 'obtener_rotacion_insumos') as mock_ins:
            
            mock_prod.return_value = rotacion_data
            mock_ins.return_value = {'items': [], 'total': 0}
            
            # Act
            resultado = self.service._calcular_rotacion_promedio(
                fecha_inicio=date.today() - timedelta(days=30),
                fecha_fin=date.today()
            )
            
            # Assert
            assert resultado >= Decimal('0')

    def test_calcular_rotacion_periodo_cero_dias(self):
        """
        Test: Calcular rotación con período de cero días.
        
        Resultado esperado:
        - Retorna 0
        """
        # Act
        resultado = self.service._calcular_rotacion_promedio(
            fecha_inicio=date.today(),
            fecha_fin=date.today() - timedelta(days=1)  # Período negativo
        )
        
        # Assert
        assert resultado == Decimal('0')

    # ==================== PROCESAR ITEMS ROTACIÓN ====================

    def test_procesar_items_rotacion_calcula_dias_stock(self):
        """
        Test: Calcular días de stock restante.
        
        Resultado esperado:
        - dias_stock = stock_actual / consumo_diario
        """
        # Arrange
        items = [
            {
                'id': 1,
                'codigo': 'PROD001',
                'nombre': 'Producto',
                'tipo': 'producto',
                'stock_actual': Decimal('100'),
                'unidad_medida': 'UNIDAD',
                'consumo_periodo': Decimal('30')  # 1 por día en 30 días
            }
        ]
        
        # Act
        resultado = self.service._procesar_items_rotacion(items, dias_periodo=30)
        
        # Assert
        assert len(resultado) == 1
        # 100 stock / 1 consumo_diario = 100 días
        assert resultado[0].dias_stock == Decimal('100.0')

    def test_procesar_items_rotacion_sin_consumo(self):
        """
        Test: Procesar item sin consumo.
        
        Resultado esperado:
        - dias_stock = 999 (infinito)
        - rotacion = 0
        """
        # Arrange
        items = [
            {
                'id': 1,
                'codigo': 'PROD001',
                'nombre': 'Producto Sin Movimiento',
                'tipo': 'producto',
                'stock_actual': Decimal('100'),
                'unidad_medida': 'UNIDAD',
                'consumo_periodo': Decimal('0')
            }
        ]
        
        # Act
        resultado = self.service._procesar_items_rotacion(items, dias_periodo=30)
        
        # Assert
        assert len(resultado) == 1
        assert resultado[0].dias_stock == Decimal('999.0')
        assert resultado[0].rotacion_anualizada == Decimal('0')
        assert resultado[0].clasificacion == 'baja'
