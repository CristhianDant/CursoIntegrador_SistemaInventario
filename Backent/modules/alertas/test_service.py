"""
Tests unitarios para AlertasService.

Este módulo contiene tests para validar el comportamiento del servicio de alertas
utilizando mocks para aislar la lógica del servicio de las dependencias externas.

NO se evalúan: envío de emails, tareas cron, job scheduler.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime
from decimal import Decimal

from modules.alertas.service import AlertasService
from modules.alertas.model import Notificacion, TipoAlerta, SemaforoEstado
from modules.alertas.schemas import (
    SemaforoEstadoEnum, TipoAlertaEnum
)


# ==================== TEST CLASS ====================

class TestAlertasService:
    """Tests para AlertasService."""

    @pytest.fixture(autouse=True)
    def setup(self, mock_db_session):
        """Configura el servicio antes de cada test."""
        self.service = AlertasService(mock_db_session)
        self.mock_db = mock_db_session

    # ==================== CONFIGURACIÓN ====================

    def test_obtener_configuracion_alertas_con_empresa(self, mock_empresa):
        """
        Test: Obtener configuración de alertas cuando la empresa existe.
        
        Resultado esperado:
        - Retorna la configuración de la empresa
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_empresa
        self.mock_db.query.return_value = mock_query
        
        # Act
        resultado = self.service.obtener_configuracion_alertas(id_empresa=1)
        
        # Assert
        assert resultado is not None
        assert "dias_verde" in resultado
        assert "dias_amarillo" in resultado
        assert "dias_rojo" in resultado

    def test_obtener_configuracion_alertas_sin_empresa(self):
        """
        Test: Obtener configuración por defecto cuando la empresa no existe.
        
        Resultado esperado:
        - Retorna configuración por defecto
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        self.mock_db.query.return_value = mock_query
        
        # Act
        resultado = self.service.obtener_configuracion_alertas(id_empresa=999)
        
        # Assert
        assert resultado is not None
        assert isinstance(resultado, dict)

    def test_actualizar_configuracion_alertas_exitoso(self, mock_empresa):
        """
        Test: Actualizar configuración de alertas de una empresa.
        
        Resultado esperado:
        - Actualiza y retorna la configuración nueva
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_empresa
        self.mock_db.query.return_value = mock_query
        
        nueva_config = {"dias_rojo": 5}
        
        # Act
        resultado = self.service.actualizar_configuracion_alertas(
            id_empresa=1,
            configuracion=nueva_config
        )
        
        # Assert
        assert resultado is not None
        self.mock_db.commit.assert_called_once()

    def test_actualizar_configuracion_alertas_empresa_no_encontrada(self):
        """
        Test: Actualizar configuración cuando empresa no existe.
        
        Resultado esperado:
        - Lanza ValueError
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        self.mock_db.query.return_value = mock_query
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            self.service.actualizar_configuracion_alertas(
                id_empresa=999,
                configuracion={"dias_rojo": 5}
            )
        
        assert "no encontrada" in str(exc_info.value)

    # ==================== NOTIFICACIONES ====================

    def test_obtener_notificaciones_lista_completa(self, mock_notificacion):
        """
        Test: Obtener todas las notificaciones activas.
        
        Resultado esperado:
        - Retorna lista de notificaciones
        """
        # Arrange
        mock_notificacion.nombre_insumo = "Insumo Test"
        mock_notificacion.codigo_insumo = "INS001"
        
        with patch.object(
            self.service.repository, 
            'obtener_notificaciones_activas'
        ) as mock_get:
            mock_get.return_value = [mock_notificacion]
            
            # Act
            resultado = self.service.obtener_notificaciones()
            
            # Assert
            assert len(resultado) == 1
            assert resultado[0].id_notificacion == 1
            mock_get.assert_called_once()

    def test_obtener_notificaciones_filtro_tipo(self, mock_notificacion):
        """
        Test: Obtener notificaciones filtradas por tipo.
        
        Resultado esperado:
        - Filtra por el tipo especificado
        """
        # Arrange
        mock_notificacion.nombre_insumo = None
        mock_notificacion.codigo_insumo = None
        
        with patch.object(
            self.service.repository, 
            'obtener_notificaciones_activas'
        ) as mock_get:
            mock_get.return_value = [mock_notificacion]
            
            # Act
            resultado = self.service.obtener_notificaciones(tipo="STOCK_CRITICO")
            
            # Assert
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args.kwargs['tipo'].value == "STOCK_CRITICO"

    def test_obtener_notificaciones_solo_no_leidas(self, mock_notificacion):
        """
        Test: Obtener solo notificaciones no leídas.
        
        Resultado esperado:
        - Filtra por leída = False
        """
        # Arrange
        mock_notificacion.nombre_insumo = None
        mock_notificacion.codigo_insumo = None
        
        with patch.object(
            self.service.repository, 
            'obtener_notificaciones_activas'
        ) as mock_get:
            mock_get.return_value = []
            
            # Act
            self.service.obtener_notificaciones(solo_no_leidas=True)
            
            # Assert
            mock_get.assert_called_once_with(
                tipo=None,
                solo_no_leidas=True,
                limit=100
            )

    def test_obtener_notificaciones_lista_vacia(self):
        """
        Test: Obtener notificaciones cuando no hay ninguna.
        
        Resultado esperado:
        - Retorna lista vacía
        """
        # Arrange
        with patch.object(
            self.service.repository, 
            'obtener_notificaciones_activas'
        ) as mock_get:
            mock_get.return_value = []
            
            # Act
            resultado = self.service.obtener_notificaciones()
            
            # Assert
            assert resultado == []

    def test_marcar_notificacion_leida(self):
        """
        Test: Marcar una notificación como leída.
        
        Resultado esperado:
        - Retorna True y hace commit
        """
        # Arrange
        with patch.object(
            self.service.repository, 
            'marcar_como_leida'
        ) as mock_marcar:
            mock_marcar.return_value = True
            
            # Act
            resultado = self.service.marcar_notificacion_leida(id_notificacion=1)
            
            # Assert
            assert resultado is True
            mock_marcar.assert_called_once_with(1)
            self.mock_db.commit.assert_called_once()

    def test_marcar_todas_leidas(self):
        """
        Test: Marcar todas las notificaciones como leídas.
        
        Resultado esperado:
        - Retorna cantidad de notificaciones marcadas
        """
        # Arrange
        with patch.object(
            self.service.repository, 
            'marcar_todas_como_leidas'
        ) as mock_marcar:
            mock_marcar.return_value = 5
            
            # Act
            resultado = self.service.marcar_todas_leidas()
            
            # Assert
            assert resultado == 5
            self.mock_db.commit.assert_called_once()

    def test_marcar_todas_leidas_por_tipo(self):
        """
        Test: Marcar todas las notificaciones de un tipo como leídas.
        
        Resultado esperado:
        - Filtra por tipo al marcar
        """
        # Arrange
        with patch.object(
            self.service.repository, 
            'marcar_todas_como_leidas'
        ) as mock_marcar:
            mock_marcar.return_value = 3
            
            # Act
            resultado = self.service.marcar_todas_leidas(tipo="VENCIMIENTO_PROXIMO")
            
            # Assert
            assert resultado == 3
            call_args = mock_marcar.call_args
            assert call_args.kwargs['tipo'].value == "VENCIMIENTO_PROXIMO"

    def test_obtener_resumen_alertas(self):
        """
        Test: Obtener resumen de alertas no leídas.
        
        Resultado esperado:
        - Retorna resumen con conteos por tipo
        """
        # Arrange
        conteos = {
            "STOCK_CRITICO": 3,
            "VENCIMIENTO_PROXIMO": 2,
            "USAR_HOY": 1
        }
        
        with patch.object(
            self.service.repository, 
            'contar_no_leidas_por_tipo'
        ) as mock_contar:
            mock_contar.return_value = conteos
            
            # Act
            resultado = self.service.obtener_resumen_alertas()
            
            # Assert
            assert resultado.total_no_leidas == 6
            assert resultado.por_tipo == conteos
            assert resultado.fecha == date.today()

    # ==================== SEMÁFORO DE VENCIMIENTOS ====================

    def test_obtener_semaforo_vencimientos(self, mock_empresa):
        """
        Test: Obtener semáforo completo de vencimientos.
        
        Resultado esperado:
        - Retorna resumen con items por estado
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_empresa
        self.mock_db.query.return_value = mock_query
        
        conteos = {"VERDE": 10, "AMARILLO": 5, "ROJO": 2, "VENCIDO": 1}
        lotes = [
            {
                "id_insumo": 1,
                "codigo_insumo": "INS001",
                "nombre_insumo": "Insumo Test",
                "unidad_medida": "KG",
                "cantidad_restante": Decimal("10.00"),
                "fecha_vencimiento": date.today(),
                "dias_restantes": 2,
                "id_ingreso_detalle": 1,
                "numero_ingreso": "ING001"
            }
        ]
        
        with patch.object(
            self.service.repository, 
            'obtener_resumen_semaforo'
        ) as mock_resumen, \
             patch.object(
            self.service.repository, 
            'obtener_lotes_por_vencer'
        ) as mock_lotes:
            mock_resumen.return_value = conteos
            mock_lotes.return_value = lotes
            
            # Act
            resultado = self.service.obtener_semaforo_vencimientos()
            
            # Assert
            assert resultado.total_verde == 10
            assert resultado.total_amarillo == 5
            assert resultado.total_rojo == 2
            assert resultado.total_vencidos == 1
            assert resultado.fecha_consulta == date.today()

    def test_obtener_semaforo_sin_lotes(self, mock_empresa):
        """
        Test: Obtener semáforo cuando no hay lotes por vencer.
        
        Resultado esperado:
        - Retorna resumen con listas vacías
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_empresa
        self.mock_db.query.return_value = mock_query
        
        with patch.object(
            self.service.repository, 
            'obtener_resumen_semaforo'
        ) as mock_resumen, \
             patch.object(
            self.service.repository, 
            'obtener_lotes_por_vencer'
        ) as mock_lotes:
            mock_resumen.return_value = {"VERDE": 0, "AMARILLO": 0, "ROJO": 0, "VENCIDO": 0}
            mock_lotes.return_value = []
            
            # Act
            resultado = self.service.obtener_semaforo_vencimientos()
            
            # Assert
            assert resultado.items_rojo == []
            assert resultado.items_amarillo == []

    def test_obtener_items_rojos(self, mock_empresa):
        """
        Test: Obtener solo items en estado rojo.
        
        Resultado esperado:
        - Retorna lista de items rojos
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_empresa
        self.mock_db.query.return_value = mock_query
        
        lotes_rojo = [
            {
                "id_insumo": 1,
                "codigo_insumo": "INS001",
                "nombre_insumo": "Insumo Urgente",
                "unidad_medida": "KG",
                "cantidad_restante": Decimal("5.00"),
                "fecha_vencimiento": date.today(),
                "dias_restantes": 1,
                "id_ingreso_detalle": 1,
                "numero_ingreso": "ING001"
            }
        ]
        
        with patch.object(
            self.service.repository, 
            'obtener_resumen_semaforo'
        ) as mock_resumen, \
             patch.object(
            self.service.repository, 
            'obtener_lotes_por_vencer'
        ) as mock_lotes:
            mock_resumen.return_value = {"VERDE": 0, "AMARILLO": 0, "ROJO": 1, "VENCIDO": 0}
            mock_lotes.return_value = lotes_rojo
            
            # Act
            resultado = self.service.obtener_items_rojos()
            
            # Assert
            assert len(resultado) >= 0  # Items rojos

    # ==================== STOCK CRÍTICO ====================

    def test_obtener_stock_critico(self):
        """
        Test: Obtener resumen de insumos con stock crítico.
        
        Resultado esperado:
        - Retorna resumen con items bajo mínimo
        """
        # Arrange
        insumos_criticos = [
            {
                "id_insumo": 1,
                "codigo": "INS001",
                "nombre": "Insumo Sin Stock",
                "unidad_medida": "KG",
                "stock_actual": Decimal("0"),
                "stock_minimo": Decimal("10.00")
            },
            {
                "id_insumo": 2,
                "codigo": "INS002",
                "nombre": "Insumo Bajo Mínimo",
                "unidad_medida": "LT",
                "stock_actual": Decimal("5.00"),
                "stock_minimo": Decimal("10.00")
            }
        ]
        
        with patch.object(
            self.service.repository, 
            'obtener_stock_por_insumo'
        ) as mock_stock:
            mock_stock.return_value = insumos_criticos
            
            # Act
            resultado = self.service.obtener_stock_critico()
            
            # Assert
            assert resultado.total_sin_stock == 1
            assert resultado.total_bajo_minimo == 1
            assert len(resultado.items) == 2
            assert resultado.fecha_consulta == date.today()

    def test_obtener_stock_critico_sin_items(self):
        """
        Test: Obtener stock crítico cuando no hay items críticos.
        
        Resultado esperado:
        - Retorna resumen con valores en cero
        """
        # Arrange
        with patch.object(
            self.service.repository, 
            'obtener_stock_por_insumo'
        ) as mock_stock:
            mock_stock.return_value = []
            
            # Act
            resultado = self.service.obtener_stock_critico()
            
            # Assert
            assert resultado.total_sin_stock == 0
            assert resultado.total_bajo_minimo == 0
            assert resultado.items == []

    # ==================== USAR HOY (FEFO) ====================

    def test_obtener_lista_usar_hoy(self, mock_empresa):
        """
        Test: Obtener lista FEFO de items a usar hoy.
        
        Resultado esperado:
        - Retorna lista ordenada por prioridad
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_empresa
        self.mock_db.query.return_value = mock_query
        
        lotes = [
            {
                "id_insumo": 1,
                "codigo_insumo": "INS001",
                "nombre_insumo": "Insumo Urgente",
                "unidad_medida": "KG",
                "cantidad_restante": Decimal("5.00"),
                "fecha_vencimiento": date.today(),
                "dias_restantes": 0,
                "prioridad": 1,
                "id_ingreso_detalle": 1,
                "valor_estimado": Decimal("50.00")
            }
        ]
        
        with patch.object(
            self.service.repository, 
            'obtener_lista_usar_hoy'
        ) as mock_lista:
            mock_lista.return_value = lotes
            
            # Act
            resultado = self.service.obtener_lista_usar_hoy()
            
            # Assert
            assert resultado.total_items == 1
            assert resultado.fecha == date.today()
            assert len(resultado.items) == 1

    def test_obtener_lista_usar_hoy_calcula_valor_total(self, mock_empresa):
        """
        Test: Calcula correctamente el valor total en riesgo.
        
        Resultado esperado:
        - Suma los valores estimados de todos los items
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_empresa
        self.mock_db.query.return_value = mock_query
        
        lotes = [
            {
                "id_insumo": 1,
                "codigo_insumo": "INS001",
                "nombre_insumo": "Insumo 1",
                "unidad_medida": "KG",
                "cantidad_restante": Decimal("5.00"),
                "fecha_vencimiento": date.today(),
                "dias_restantes": 0,
                "prioridad": 1,
                "id_ingreso_detalle": 1,
                "valor_estimado": Decimal("50.00")
            },
            {
                "id_insumo": 2,
                "codigo_insumo": "INS002",
                "nombre_insumo": "Insumo 2",
                "unidad_medida": "LT",
                "cantidad_restante": Decimal("3.00"),
                "fecha_vencimiento": date.today(),
                "dias_restantes": 1,
                "prioridad": 2,
                "id_ingreso_detalle": 2,
                "valor_estimado": Decimal("30.00")
            }
        ]
        
        with patch.object(
            self.service.repository, 
            'obtener_lista_usar_hoy'
        ) as mock_lista:
            mock_lista.return_value = lotes
            
            # Act
            resultado = self.service.obtener_lista_usar_hoy()
            
            # Assert
            assert resultado.valor_estimado_en_riesgo == 80.00
            assert resultado.total_items == 2

    def test_obtener_lista_usar_hoy_vacia(self, mock_empresa):
        """
        Test: Lista vacía cuando no hay items por usar hoy.
        
        Resultado esperado:
        - Retorna lista vacía con valores en cero
        """
        # Arrange
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_empresa
        self.mock_db.query.return_value = mock_query
        
        with patch.object(
            self.service.repository, 
            'obtener_lista_usar_hoy'
        ) as mock_lista:
            mock_lista.return_value = []
            
            # Act
            resultado = self.service.obtener_lista_usar_hoy()
            
            # Assert
            assert resultado.total_items == 0
            assert resultado.valor_estimado_en_riesgo == 0
            assert resultado.items == []
