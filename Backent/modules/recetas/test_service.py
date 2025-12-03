"""
Tests unitarios para RecetaService.

Este módulo contiene tests para validar el comportamiento del servicio de recetas
utilizando mocks para aislar la lógica del servicio de las dependencias externas.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from fastapi import HTTPException
from decimal import Decimal
import datetime

from modules.recetas.service import RecetaService
from modules.recetas.model import Receta as RecetaModel, RecetaDetalle as RecetaDetalleModel
from modules.recetas.schemas import RecetaCreate, RecetaUpdate, RecetaDetalleCreate, RecetaDetalleUpdate
from enums.estado import EstadoEnum


# ==================== FIXTURES ====================

@pytest.fixture
def mock_db_session():
    """Mock de sesión de base de datos."""
    session = MagicMock()
    session.commit = Mock()
    session.rollback = Mock()
    session.refresh = Mock()
    session.add = Mock()
    session.query = Mock()
    return session


@pytest.fixture
def mock_receta_detalle():
    """Mock de un detalle de receta."""
    detalle = MagicMock(spec=RecetaDetalleModel)
    detalle.id_receta_detalle = 1
    detalle.id_receta = 1
    detalle.id_insumo = 10
    detalle.cantidad = Decimal("2.5")
    detalle.costo_unitario = Decimal("5.00")
    detalle.costo_total = Decimal("12.50")
    detalle.es_opcional = False
    detalle.observaciones = "Detalle de prueba"
    return detalle


@pytest.fixture
def mock_receta(mock_receta_detalle):
    """Mock de una receta completa."""
    receta = MagicMock(spec=RecetaModel)
    receta.id_receta = 1
    receta.id_producto = 100
    receta.codigo_receta = "REC-001"
    receta.nombre_receta = "Receta de Prueba"
    receta.descripcion = "Descripción de la receta de prueba"
    receta.rendimiento_producto_terminado = Decimal("10.0000")
    receta.costo_estimado = Decimal("50.00")
    receta.fecha_creacion = datetime.datetime(2025, 1, 1, 12, 0, 0)
    receta.version = Decimal("1.0")
    receta.estado = EstadoEnum.ACTIVA
    receta.anulado = False
    receta.detalles = [mock_receta_detalle]
    return receta


@pytest.fixture
def mock_receta_create():
    """Mock de datos para crear una receta."""
    return RecetaCreate(
        id_producto=100,
        codigo_receta="REC-002",
        nombre_receta="Nueva Receta",
        descripcion="Descripción de nueva receta",
        rendimiento_producto_terminado=Decimal("5.0000"),
        costo_estimado=Decimal("25.00"),
        version=Decimal("1.0"),
        estado=EstadoEnum.ACTIVA,
        detalles=[
            RecetaDetalleCreate(
                id_insumo=10,
                cantidad=Decimal("1.5"),
                costo_unitario=Decimal("10.00"),
                costo_total=Decimal("15.00"),
                es_opcional=False,
                observaciones="Detalle nuevo"
            )
        ]
    )


@pytest.fixture
def mock_receta_update():
    """Mock de datos para actualizar una receta."""
    return RecetaUpdate(
        id_producto=100,
        codigo_receta="REC-001-UPD",
        nombre_receta="Receta Actualizada",
        descripcion="Descripción actualizada",
        rendimiento_producto_terminado=Decimal("15.0000"),
        costo_estimado=Decimal("75.00"),
        version=Decimal("2.0"),
        estado=EstadoEnum.ACTIVA,
        detalles=[
            RecetaDetalleUpdate(
                id_insumo=10,
                cantidad=Decimal("3.0"),
                costo_unitario=Decimal("10.00"),
                costo_total=Decimal("30.00"),
                es_opcional=True,
                observaciones="Detalle actualizado"
            )
        ]
    )


# ==================== TEST CLASS ====================

class TestRecetaService:
    """Tests para RecetaService."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura el servicio antes de cada test."""
        self.service = RecetaService()

    # -------------------- GET ALL --------------------

    def test_get_all_retorna_lista_recetas(self, mock_db_session, mock_receta):
        """
        Test: Obtener todas las recetas.
        
        Resultado esperado:
        - Retorna una lista con todas las recetas
        - El repository.get_all es llamado una vez con db_session
        """
        # Arrange
        lista_recetas = [mock_receta]
        with patch.object(self.service.repository, 'get_all') as mock_get_all:
            mock_get_all.return_value = lista_recetas

            # Act
            resultado = self.service.get_all(db=mock_db_session)

            # Assert
            assert resultado == lista_recetas
            assert len(resultado) == 1
            mock_get_all.assert_called_once_with(mock_db_session)

    def test_get_all_retorna_lista_vacia(self, mock_db_session):
        """
        Test: Obtener todas las recetas cuando no hay ninguna.
        
        Resultado esperado:
        - Retorna una lista vacía
        """
        # Arrange
        with patch.object(self.service.repository, 'get_all') as mock_get_all:
            mock_get_all.return_value = []

            # Act
            resultado = self.service.get_all(db=mock_db_session)

            # Assert
            assert resultado == []
            assert len(resultado) == 0
            mock_get_all.assert_called_once_with(mock_db_session)

    # -------------------- GET BY ID --------------------

    def test_get_by_id_existente(self, mock_db_session, mock_receta):
        """
        Test: Obtener receta por ID cuando existe.
        
        Resultado esperado:
        - Retorna la receta solicitada
        - El repository.get_by_id es llamado con el ID correcto
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = mock_receta

            # Act
            resultado = self.service.get_by_id(db=mock_db_session, receta_id=1)

            # Assert
            assert resultado.id_receta == 1
            assert resultado.nombre_receta == "Receta de Prueba"
            mock_get_by_id.assert_called_once_with(mock_db_session, 1)

    def test_get_by_id_no_existente(self, mock_db_session):
        """
        Test: Obtener receta por ID cuando no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        - Mensaje: "Receta no encontrada"
        """
        # Arrange
        with patch.object(self.service.repository, 'get_by_id') as mock_get_by_id:
            mock_get_by_id.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.get_by_id(db=mock_db_session, receta_id=999)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Receta no encontrada"
            mock_get_by_id.assert_called_once_with(mock_db_session, 999)

    # -------------------- CREATE --------------------

    def test_create_exitoso(self, mock_db_session, mock_receta_create, mock_receta):
        """
        Test: Crear receta exitosamente cuando todos los insumos existen.
        
        Resultado esperado:
        - Retorna la receta creada
        - InsumoService valida que el insumo existe
        - repository.create es llamado con los datos correctos
        """
        # Arrange
        mock_insumo = MagicMock()
        mock_insumo.id_insumo = 10

        with patch.object(self.service.repository, 'create') as mock_create, \
             patch('modules.recetas.service.InsumoService') as MockInsumoService:
            
            mock_insumo_service_instance = MockInsumoService.return_value
            mock_insumo_service_instance.get_insumo.return_value = mock_insumo
            mock_create.return_value = mock_receta

            # Act
            resultado = self.service.create(db=mock_db_session, receta=mock_receta_create)

            # Assert
            assert resultado.id_receta == 1
            mock_insumo_service_instance.get_insumo.assert_called_once_with(10)
            mock_create.assert_called_once_with(mock_db_session, mock_receta_create)

    def test_create_insumo_no_existe(self, mock_db_session, mock_receta_create):
        """
        Test: Crear receta falla cuando un insumo no existe.
        
        Resultado esperado:
        - Lanza Exception con mensaje indicando el insumo que no existe
        - repository.create NO es llamado
        """
        # Arrange
        with patch.object(self.service.repository, 'create') as mock_create, \
             patch('modules.recetas.service.InsumoService') as MockInsumoService:
            
            mock_insumo_service_instance = MockInsumoService.return_value
            mock_insumo_service_instance.get_insumo.return_value = None

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                self.service.create(db=mock_db_session, receta=mock_receta_create)

            assert "El insumo con id 10 no existe" in str(exc_info.value)
            mock_create.assert_not_called()

    def test_create_multiples_insumos_uno_no_existe(self, mock_db_session):
        """
        Test: Crear receta con múltiples insumos donde el segundo no existe.
        
        Resultado esperado:
        - Lanza Exception indicando el insumo que no existe
        - Valida cada insumo en orden
        """
        # Arrange
        receta_create = RecetaCreate(
            id_producto=100,
            codigo_receta="REC-003",
            nombre_receta="Receta Multi Insumos",
            descripcion="Receta con múltiples insumos",
            rendimiento_producto_terminado=Decimal("10.0000"),
            detalles=[
                RecetaDetalleCreate(id_insumo=10, cantidad=Decimal("1.0")),
                RecetaDetalleCreate(id_insumo=20, cantidad=Decimal("2.0")),
            ]
        )

        mock_insumo_1 = MagicMock()
        mock_insumo_1.id_insumo = 10

        with patch.object(self.service.repository, 'create') as mock_create, \
             patch('modules.recetas.service.InsumoService') as MockInsumoService:
            
            mock_insumo_service_instance = MockInsumoService.return_value
            # Primer insumo existe, segundo no
            mock_insumo_service_instance.get_insumo.side_effect = [mock_insumo_1, None]

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                self.service.create(db=mock_db_session, receta=receta_create)

            assert "El insumo con id 20 no existe" in str(exc_info.value)
            mock_create.assert_not_called()

    # -------------------- UPDATE --------------------

    def test_update_exitoso(self, mock_db_session, mock_receta_update, mock_receta):
        """
        Test: Actualizar receta exitosamente.
        
        Resultado esperado:
        - Retorna la receta actualizada
        - repository.update es llamado con ID y datos correctos
        """
        # Arrange
        mock_receta.nombre_receta = "Receta Actualizada"
        
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = mock_receta

            # Act
            resultado = self.service.update(
                db=mock_db_session,
                receta_id=1,
                receta=mock_receta_update
            )

            # Assert
            assert resultado.nombre_receta == "Receta Actualizada"
            mock_update.assert_called_once_with(mock_db_session, 1, mock_receta_update)

    def test_update_receta_no_existente(self, mock_db_session, mock_receta_update):
        """
        Test: Actualizar receta que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        - Mensaje: "Receta no encontrada"
        """
        # Arrange
        with patch.object(self.service.repository, 'update') as mock_update:
            mock_update.return_value = None

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.update(
                    db=mock_db_session,
                    receta_id=999,
                    receta=mock_receta_update
                )

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Receta no encontrada"
            mock_update.assert_called_once_with(mock_db_session, 999, mock_receta_update)

    # -------------------- DELETE --------------------

    def test_delete_exitoso(self, mock_db_session):
        """
        Test: Eliminar (anular) receta exitosamente.
        
        Resultado esperado:
        - Retorna mensaje de éxito
        - repository.delete es llamado con el ID correcto
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = True

            # Act
            resultado = self.service.delete(db=mock_db_session, receta_id=1)

            # Assert
            assert resultado == {"message": "Receta anulada correctamente"}
            mock_delete.assert_called_once_with(mock_db_session, 1)

    def test_delete_receta_no_existente(self, mock_db_session):
        """
        Test: Eliminar receta que no existe.
        
        Resultado esperado:
        - Lanza HTTPException con status 404
        - Mensaje: "Receta no encontrada"
        """
        # Arrange
        with patch.object(self.service.repository, 'delete') as mock_delete:
            mock_delete.return_value = False

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                self.service.delete(db=mock_db_session, receta_id=999)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Receta no encontrada"
            mock_delete.assert_called_once_with(mock_db_session, 999)
