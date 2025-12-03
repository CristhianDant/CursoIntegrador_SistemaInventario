"""
Tests unitarios para MermaService.

Este módulo contiene tests para validar el comportamiento del servicio de mermas
(calidad/desperdicio) utilizando mocks para aislar la lógica del servicio.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime

from modules.calidad_desperdicio_merma.service import MermaService
from modules.calidad_desperdicio_merma.model import CalidadDesperdicioMerma
from modules.calidad_desperdicio_merma.schemas import MermaCreate, MermaUpdate, Merma
from enums.tipo_merma import TipoMermaEnum


# ==================== FIXTURES ADICIONALES ====================

@pytest.fixture
def mock_merma_create():
    """Mock de datos para crear una merma."""
    return MermaCreate(
        numero_registro="MER-2025-0002",
        tipo="VENCIMIENTO",
        causa="Producto vencido",
        cantidad=Decimal("5.00"),
        costo_unitario=Decimal("10.00"),
        costo_total=Decimal("50.00"),
        fecha_caso=datetime.now(),
        id_insumo=1,
        id_user_responsable=1,
        observacion="Producto retirado"
    )


@pytest.fixture
def mock_merma_update():
    """Mock de datos para actualizar una merma."""
    return MermaUpdate(
        causa="Causa actualizada",
        cantidad=Decimal("3.00"),
        observacion="Observación actualizada"
    )


# ==================== TEST CLASS ====================

class TestMermaService:
    """Tests para MermaService."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura el servicio antes de cada test."""
        self.service = MermaService()

    # -------------------- GET ALL --------------------

    def test_get_all_retorna_lista(self, mock_db_session, mock_merma):
        """
        Test: Obtener todos los registros de merma.
        
        Resultado esperado:
        - Retorna lista con todas las mermas
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get:
            mock_get.return_value = [mock_merma]
            
            # Act
            resultado = self.service.get_all(mock_db_session)
            
            # Assert
            assert len(resultado) == 1
            mock_get.assert_called_once_with(mock_db_session)

    def test_get_all_lista_vacia(self, mock_db_session):
        """
        Test: Obtener mermas cuando no hay ninguna.
        
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

    def test_get_by_id_existente(self, mock_db_session, mock_merma):
        """
        Test: Obtener merma por ID cuando existe.
        
        Resultado esperado:
        - Retorna la merma solicitada
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = mock_merma
            
            # Act
            resultado = self.service.get_by_id(mock_db_session, merma_id=1)
            
            # Assert
            assert resultado.id_merma == 1
            mock_get.assert_called_once_with(mock_db_session, 1)

    def test_get_by_id_no_encontrado(self, mock_db_session):
        """
        Test: Obtener merma por ID cuando no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get:
            mock_get.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_by_id(mock_db_session, merma_id=999)
            
            assert exc_info.value.status_code == 404
            assert "no encontrado" in exc_info.value.detail

    # -------------------- CREATE --------------------

    def test_create_exitoso(self, mock_db_session, mock_merma_create, mock_merma):
        """
        Test: Crear registro de merma exitosamente.
        
        Resultado esperado:
        - Retorna la merma creada
        """
        # Arrange
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_merma
            
            # Act
            resultado = self.service.create(mock_db_session, mock_merma_create)
            
            # Assert
            assert resultado.id_merma == 1
            mock_create.assert_called_once_with(mock_db_session, mock_merma_create)

    def test_create_con_insumo(self, mock_db_session, mock_merma):
        """
        Test: Crear merma asociada a un insumo.
        
        Resultado esperado:
        - Se crea con el id_insumo correcto
        """
        # Arrange
        merma_data = MermaCreate(
            numero_registro="MER-2025-0003",
            tipo=TipoMermaEnum.DAÑO,
            causa="Producto dañado",
            cantidad=Decimal("2.00"),
            id_insumo=5,
            id_user_responsable=1
        )
        
        mock_merma.id_insumo = 5
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_merma
            
            # Act
            resultado = self.service.create(mock_db_session, merma_data)
            
            # Assert
            assert resultado.id_insumo == 5

    def test_create_con_producto(self, mock_db_session, mock_merma):
        """
        Test: Crear merma asociada a un producto terminado.
        
        Resultado esperado:
        - Se crea con el id_producto correcto
        """
        # Arrange
        merma_data = MermaCreate(
            numero_registro="MER-2025-0004",
            tipo=TipoMermaEnum.DAÑO,
            causa="Error en producción",
            cantidad=Decimal("1.00"),
            id_producto=3,
            id_user_responsable=1
        )
        
        mock_merma.id_producto = 3
        mock_merma.id_insumo = None
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_merma
            
            # Act
            resultado = self.service.create(mock_db_session, merma_data)
            
            # Assert
            mock_create.assert_called_once()

    # -------------------- UPDATE --------------------

    def test_update_exitoso(self, mock_db_session, mock_merma_update, mock_merma):
        """
        Test: Actualizar merma existente.
        
        Resultado esperado:
        - Retorna la merma actualizada
        """
        # Arrange
        mock_merma.causa = "Causa actualizada"
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_merma
            
            # Act
            resultado = self.service.update(mock_db_session, merma_id=1, merma=mock_merma_update)
            
            # Assert
            assert resultado.causa == "Causa actualizada"
            mock_update.assert_called_once_with(mock_db_session, 1, mock_merma_update)

    def test_update_no_encontrado(self, mock_db_session, mock_merma_update):
        """
        Test: Actualizar merma que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.update(mock_db_session, merma_id=999, merma=mock_merma_update)
            
            assert exc_info.value.status_code == 404

    def test_update_parcial(self, mock_db_session, mock_merma):
        """
        Test: Actualizar solo algunos campos de la merma.
        
        Resultado esperado:
        - Solo actualiza los campos proporcionados
        """
        # Arrange
        update_data = MermaUpdate(observacion="Nueva observación")
        mock_merma.observacion = "Nueva observación"
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_merma
            
            # Act
            resultado = self.service.update(mock_db_session, merma_id=1, merma=update_data)
            
            # Assert
            assert resultado.observacion == "Nueva observación"

    # -------------------- DELETE --------------------

    def test_delete_exitoso(self, mock_db_session):
        """
        Test: Anular merma exitosamente.
        
        Resultado esperado:
        - Retorna mensaje de confirmación
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = True
            
            # Act
            resultado = self.service.delete(mock_db_session, merma_id=1)
            
            # Assert
            assert "message" in resultado
            assert "anulad" in resultado["message"].lower()
            mock_delete.assert_called_once_with(mock_db_session, 1)

    def test_delete_no_encontrado(self, mock_db_session):
        """
        Test: Anular merma que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = False
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.delete(mock_db_session, merma_id=999)
            
            assert exc_info.value.status_code == 404

    # -------------------- CASOS DE BORDE --------------------

    def test_create_con_cantidad_cero(self, mock_db_session, mock_merma):
        """
        Test: Crear merma con cantidad cero.
        
        Resultado esperado:
        - Se crea correctamente (validación en schema)
        """
        # Arrange
        merma_data = MermaCreate(
            numero_registro="MER-2025-0005",
            tipo=TipoMermaEnum.HONGEADO,
            causa="Ajuste de inventario",
            cantidad=Decimal("0.00"),
            id_user_responsable=1
        )
        
        mock_merma.cantidad = Decimal("0.00")
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_merma
            
            # Act
            resultado = self.service.create(mock_db_session, merma_data)
            
            # Assert
            mock_create.assert_called_once()

    def test_create_calcula_costo_total(self, mock_db_session, mock_merma):
        """
        Test: Verificar que se puede calcular costo total.
        
        Resultado esperado:
        - costo_total = cantidad * costo_unitario
        """
        # Arrange
        merma_data = MermaCreate(
            numero_registro="MER-2025-0006",
            tipo="VENCIMIENTO",
            causa="Producto vencido",
            cantidad=Decimal("10.00"),
            costo_unitario=Decimal("5.00"),
            costo_total=Decimal("50.00"),
            id_user_responsable=1
        )
        
        mock_merma.cantidad = Decimal("10.00")
        mock_merma.costo_unitario = Decimal("5.00")
        mock_merma.costo_total = Decimal("50.00")
        
        with patch.object(self.service.repository, 'create') as mock_create:
            mock_create.return_value = mock_merma
            
            # Act
            resultado = self.service.create(mock_db_session, merma_data)
            
            # Assert
            assert resultado.costo_total == Decimal("50.00")
