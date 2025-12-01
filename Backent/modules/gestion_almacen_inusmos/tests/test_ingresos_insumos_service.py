"""
Tests unitarios para IngresoProductoService - Lógica de negocio de ingresos.
Usa mocks para simular el repositorio y la base de datos.
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch
from fastapi import HTTPException
from modules.gestion_almacen_inusmos.ingresos_insumos.service import IngresoProductoService
from modules.gestion_almacen_inusmos.ingresos_insumos.schemas import (
    IngresoProductoCreate,
    IngresoProductoUpdate
)


class TestIngresoProductoServiceCRUD:
    """Tests para operaciones CRUD de IngresoProductoService."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup ejecutado antes de cada test."""
        self.service = IngresoProductoService()
    
    def test_get_all_ingresos(self, mock_db_session, mock_ingreso):
        """
        Test: Obtener todos los ingresos.
        
        Resultado esperado:
        - Retorna lista de ingresos
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get_all:
            mock_get_all.return_value = [mock_ingreso]
            
            # Act
            resultado = self.service.get_all(db=mock_db_session)
            
            # Assert
            assert len(resultado) == 1
            assert resultado[0].numero_ingreso == "ING-001"
            mock_get_all.assert_called_once_with(mock_db_session)
    
    def test_get_by_id_existente(self, mock_db_session, mock_ingreso):
        """
        Test: Obtener ingreso por ID cuando existe.
        
        Resultado esperado:
        - Retorna el ingreso solicitado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = mock_ingreso
            
            # Act
            resultado = self.service.get_by_id(db=mock_db_session, ingreso_id=1)
            
            # Assert
            assert resultado.id_ingreso == 1
            assert resultado.numero_ingreso == "ING-001"
            mock_get_by_id.assert_called_once_with(mock_db_session, 1)
    
    def test_get_by_id_no_encontrado(self, mock_db_session):
        """
        Test: Obtener ingreso por ID cuando NO existe.
        
        Resultado esperado:
        - Lanza HTTPException con código 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_by_id(db=mock_db_session, ingreso_id=99999)
            
            assert exc_info.value.status_code == 404
            assert "no encontrado" in str(exc_info.value.detail).lower()
    
    def test_create_ingreso(self, mock_db_session, mock_ingreso):
        """
        Test: Crear un nuevo ingreso.
        
        Resultado esperado:
        - Retorna el ingreso creado
        """
        # Arrange
        ingreso_create = Mock(spec=IngresoProductoCreate)
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_ingreso
            
            # Act
            resultado = self.service.create(db=mock_db_session, ingreso=ingreso_create)
            
            # Assert
            assert resultado.numero_ingreso == "ING-001"
            mock_create.assert_called_once_with(mock_db_session, ingreso_create)
    
    def test_update_ingreso_existente(self, mock_db_session, mock_ingreso):
        """
        Test: Actualizar ingreso existente.
        
        Resultado esperado:
        - Retorna el ingreso actualizado
        """
        # Arrange
        ingreso_update = Mock(spec=IngresoProductoUpdate)
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_ingreso
            
            # Act
            resultado = self.service.update(
                db=mock_db_session,
                ingreso_id=1,
                ingreso=ingreso_update
            )
            
            # Assert
            assert resultado.id_ingreso == 1
            mock_update.assert_called_once_with(mock_db_session, 1, ingreso_update)
    
    def test_update_ingreso_no_encontrado(self, mock_db_session):
        """
        Test: Actualizar ingreso que NO existe.
        
        Resultado esperado:
        - Lanza HTTPException con código 404
        """
        # Arrange
        ingreso_update = Mock(spec=IngresoProductoUpdate)
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.update(
                    db=mock_db_session,
                    ingreso_id=99999,
                    ingreso=ingreso_update
                )
            
            assert exc_info.value.status_code == 404
            assert "no encontrado" in str(exc_info.value.detail).lower()
    
    def test_delete_ingreso_existente(self, mock_db_session):
        """
        Test: Eliminar (anular) ingreso existente.
        
        Resultado esperado:
        - Retorna mensaje de éxito
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = True
            
            # Act
            resultado = self.service.delete(db=mock_db_session, ingreso_id=1)
            
            # Assert
            assert "anulado correctamente" in resultado["message"]
            mock_delete.assert_called_once_with(mock_db_session, 1)
    
    def test_delete_ingreso_no_encontrado(self, mock_db_session):
        """
        Test: Eliminar ingreso que NO existe.
        
        Resultado esperado:
        - Lanza HTTPException con código 404
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = False
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.delete(db=mock_db_session, ingreso_id=99999)
            
            assert exc_info.value.status_code == 404
            assert "no encontrado" in str(exc_info.value.detail).lower()


class TestIngresoProductoServiceLotesFEFO:
    """Tests para lógica de lotes FEFO."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup ejecutado antes de cada test."""
        self.service = IngresoProductoService()
    
    def test_get_lotes_fefo_insumo_existente(
        self, 
        mock_db_session,
        mock_insumo,
        mock_lotes_fefo
    ):
        """
        Test: Obtener lotes FEFO de un insumo existente.
        
        Resultado esperado:
        - Retorna información del insumo y sus lotes
        - Lotes ordenados por FEFO
        """
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock()
        
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_insumo
        
        with patch.object(self.service.repository, 'get_lotes_fefo') as mock_get_lotes:
            # Convertir dict a Mock para simular ORM objects
            lotes_mock = [Mock(**lote) for lote in mock_lotes_fefo]
            mock_get_lotes.return_value = lotes_mock
            
            # Act
            resultado = self.service.get_lotes_fefo(db=mock_db_session, id_insumo=1)
            
            # Assert
            assert resultado.id_insumo == 1
            assert resultado.nombre_insumo == "Harina de Trigo"
            assert len(resultado.lotes) == 2
            
            mock_get_lotes.assert_called_once_with(mock_db_session, 1)
    
    def test_get_lotes_fefo_insumo_no_encontrado(self, mock_db_session):
        """
        Test: Obtener lotes FEFO de insumo que NO existe.
        
        Resultado esperado:
        - Lanza HTTPException con código 404
        """
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            self.service.get_lotes_fefo(db=mock_db_session, id_insumo=99999)
        
        assert exc_info.value.status_code == 404
        assert "Insumo no encontrado" in str(exc_info.value.detail)
    
    def test_get_lotes_fefo_con_total(
        self, 
        mock_db_session,
        mock_insumo,
        mock_lotes_fefo
    ):
        """
        Test: Obtener lotes FEFO con totales y datos de proveedor.
        
        Resultado esperado:
        - Retorna info del insumo, total de stock y cantidad de lotes
        - Incluye datos del proveedor en cada lote
        """
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_insumo
        
        with patch.object(self.service.repository, 'get_lotes_fefo_con_proveedor') as mock_get_lotes:
            mock_get_lotes.return_value = mock_lotes_fefo
            
            # Act
            resultado = self.service.get_lotes_fefo_con_total(
                db=mock_db_session,
                id_insumo=1
            )
            
            # Assert
            assert resultado.id_insumo == 1
            assert resultado.codigo_insumo == "INS001"
            assert resultado.nombre_insumo == "Harina de Trigo"
            assert resultado.total_cantidad_restante == Decimal("80.00")  # 50 + 30
            assert resultado.cantidad_lotes == 2
            assert len(resultado.lotes) == 2
            
            # Verificar datos del primer lote
            lote_1 = resultado.lotes[0]
            assert lote_1.cantidad_restante == Decimal("50.00")
            assert lote_1.nombre_proveedor == "Proveedor Test S.A."
            
            mock_get_lotes.assert_called_once_with(mock_db_session, 1)
    
    def test_get_lotes_fefo_con_total_sin_stock(
        self, 
        mock_db_session,
        mock_insumo
    ):
        """
        Test: Obtener lotes FEFO cuando no hay stock (lotes vacíos).
        
        Resultado esperado:
        - total_cantidad_restante = 0
        - cantidad_lotes = 0
        - lotes = []
        """
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_insumo
        
        with patch.object(self.service.repository, 'get_lotes_fefo_con_proveedor') as mock_get_lotes:
            mock_get_lotes.return_value = []  # Sin lotes
            
            # Act
            resultado = self.service.get_lotes_fefo_con_total(
                db=mock_db_session,
                id_insumo=1
            )
            
            # Assert
            assert resultado.total_cantidad_restante == Decimal("0")
            assert resultado.cantidad_lotes == 0
            assert len(resultado.lotes) == 0
