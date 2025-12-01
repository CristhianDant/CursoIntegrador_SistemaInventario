"""
Tests unitarios para MovimientoInsumoService - Lógica de negocio de movimientos.
Usa mocks para simular el repositorio y la base de datos.
"""
import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from modules.gestion_almacen_inusmos.movimiento_insumos.service import MovimientoInsumoService
from modules.gestion_almacen_inusmos.movimiento_insumos.schemas import MovimientoInsumoCreate


class TestMovimientoInsumoServiceCRUD:
    """Tests para operaciones CRUD de MovimientoInsumoService."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup ejecutado antes de cada test."""
        self.service = MovimientoInsumoService()
    
    def test_get_all_movimientos(self, mock_db_session, mock_movimiento):
        """
        Test: Obtener todos los movimientos.
        
        Resultado esperado:
        - Retorna lista de movimientos
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get_all:
            mock_get_all.return_value = [mock_movimiento]
            
            # Act
            resultado = self.service.get_all(db=mock_db_session)
            
            # Assert
            assert len(resultado) == 1
            assert resultado[0].numero_movimiento == "MOV-001"
            assert resultado[0].tipo_movimiento == "SALIDA"
            mock_get_all.assert_called_once_with(mock_db_session)
    
    def test_get_all_movimientos_vacio(self, mock_db_session):
        """
        Test: Obtener movimientos cuando no hay ninguno.
        
        Resultado esperado:
        - Retorna lista vacía
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get_all:
            mock_get_all.return_value = []
            
            # Act
            resultado = self.service.get_all(db=mock_db_session)
            
            # Assert
            assert len(resultado) == 0
            assert isinstance(resultado, list)
    
    def test_get_by_id_existente(self, mock_db_session, mock_movimiento):
        """
        Test: Obtener movimiento por ID cuando existe.
        
        Resultado esperado:
        - Retorna el movimiento solicitado
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = mock_movimiento
            
            # Act
            resultado = self.service.get_by_id(db=mock_db_session, movimiento_id=1)
            
            # Assert
            assert resultado.id_movimiento == 1
            assert resultado.numero_movimiento == "MOV-001"
            assert resultado.tipo_movimiento == "SALIDA"
            mock_get_by_id.assert_called_once_with(mock_db_session, 1)
    
    def test_get_by_id_no_encontrado(self, mock_db_session):
        """
        Test: Obtener movimiento por ID cuando NO existe.
        
        Resultado esperado:
        - Lanza HTTPException con código 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_by_id(db=mock_db_session, movimiento_id=99999)
            
            assert exc_info.value.status_code == 404
            assert "Movimiento de insumo no encontrado" in str(exc_info.value.detail)
    
    def test_create_movimiento(self, mock_db_session, mock_movimiento):
        """
        Test: Crear un nuevo movimiento.
        
        Resultado esperado:
        - Retorna el movimiento creado
        """
        # Arrange
        movimiento_create = Mock(spec=MovimientoInsumoCreate)
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_movimiento
            
            # Act
            resultado = self.service.create(
                db=mock_db_session,
                movimiento=movimiento_create
            )
            
            # Assert
            assert resultado.numero_movimiento == "MOV-001"
            assert resultado.tipo_movimiento == "SALIDA"
            mock_create.assert_called_once_with(mock_db_session, movimiento_create)
    
    def test_create_movimiento_multiples(self, mock_db_session):
        """
        Test: Crear múltiples movimientos.
        
        Resultado esperado:
        - Cada movimiento se crea correctamente
        - Se llama al repositorio por cada uno
        """
        # Arrange
        movimiento_1 = Mock()
        movimiento_1.numero_movimiento = "MOV-001"
        movimiento_2 = Mock()
        movimiento_2.numero_movimiento = "MOV-002"
        
        movimiento_create_1 = Mock(spec=MovimientoInsumoCreate)
        movimiento_create_2 = Mock(spec=MovimientoInsumoCreate)
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.side_effect = [movimiento_1, movimiento_2]
            
            # Act
            resultado_1 = self.service.create(db=mock_db_session, movimiento=movimiento_create_1)
            resultado_2 = self.service.create(db=mock_db_session, movimiento=movimiento_create_2)
            
            # Assert
            assert resultado_1.numero_movimiento == "MOV-001"
            assert resultado_2.numero_movimiento == "MOV-002"
            assert mock_create.call_count == 2


class TestMovimientoInsumoServiceLogica:
    """Tests para lógica de negocio adicional de movimientos."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup ejecutado antes de cada test."""
        self.service = MovimientoInsumoService()
    
    def test_repository_initialization(self):
        """
        Test: Verificar que el servicio inicializa correctamente el repositorio.
        
        Resultado esperado:
        - repository no es None
        - repository es del tipo correcto
        """
        # Assert
        assert self.service.repository is not None
        from modules.gestion_almacen_inusmos.movimiento_insumos.repository import MovimientoInsumoRepository
        assert isinstance(self.service.repository, MovimientoInsumoRepository)
    
    def test_service_implements_interface(self):
        """
        Test: Verificar que el servicio implementa la interfaz correcta.
        
        Resultado esperado:
        - Servicio tiene todos los métodos de la interfaz
        """
        # Assert
        assert hasattr(self.service, 'get_all')
        assert hasattr(self.service, 'get_by_id')
        assert hasattr(self.service, 'create')
        assert callable(self.service.get_all)
        assert callable(self.service.get_by_id)
        assert callable(self.service.create)
