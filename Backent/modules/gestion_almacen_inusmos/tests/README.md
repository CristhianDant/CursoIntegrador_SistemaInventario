# Tests Unitarios - Gestión de Almacén de Insumos

Tests unitarios para la lógica de negocio del módulo de gestión de almacén de insumos.

## 📋 Descripción

Tests **unitarios puros** usando **mocks** para validar la lógica de negocio de los servicios:

- ✅ **ProduccionService**: Validación de stock, ejecución de producción, historial y trazabilidad
- ✅ **IngresoProductoService**: CRUD de ingresos, lotes FEFO
- ✅ **MovimientoInsumoService**: CRUD de movimientos

**Nota importante**: Estos tests NO requieren base de datos real. Usan mocks para simular el comportamiento del repositorio.

## 🚀 Instalación de Dependencias

Primero, instala las dependencias de testing:

```bash
# Desde la carpeta Backent
pip install -r requirements.txt
```

Las nuevas dependencias agregadas son:
- `pytest==8.3.3`: Framework de testing
- `pytest-mock==3.14.0`: Utilidades para mocking
- `pytest-cov==6.0.0`: Cobertura de código

## 🧪 Ejecutar Tests

### Ejecutar todos los tests del módulo

```bash
# Desde la carpeta Backent
pytest modules/gestion_almacen_inusmos/tests/ -v
```

### Ejecutar tests específicos

```bash
# Tests de producción
pytest modules/gestion_almacen_inusmos/tests/test_produccion_service.py -v

# Tests de ingresos
pytest modules/gestion_almacen_inusmos/tests/test_ingresos_insumos_service.py -v

# Tests de movimientos
pytest modules/gestion_almacen_inusmos/tests/test_movimiento_insumos_service.py -v
```

### Ejecutar una clase de test específica

```bash
pytest modules/gestion_almacen_inusmos/tests/test_produccion_service.py::TestProduccionServiceValidarStock -v
```

### Ejecutar un test individual

```bash
pytest modules/gestion_almacen_inusmos/tests/test_produccion_service.py::TestProduccionServiceValidarStock::test_validar_stock_receta_con_stock_suficiente -v
```

## 📊 Cobertura de Código

### Ver cobertura básica

```bash
pytest modules/gestion_almacen_inusmos/tests/ --cov=modules.gestion_almacen_inusmos
```

### Ver cobertura detallada con reporte HTML

```bash
pytest modules/gestion_almacen_inusmos/tests/ --cov=modules.gestion_almacen_inusmos --cov-report=html
```

Luego abre `htmlcov/index.html` en tu navegador.

### Ver líneas no cubiertas

```bash
pytest modules/gestion_almacen_inusmos/tests/ --cov=modules.gestion_almacen_inusmos --cov-report=term-missing
```

## 📁 Estructura de Tests

```
modules/gestion_almacen_inusmos/tests/
├── __init__.py                          # Inicialización del paquete
├── conftest.py                          # Fixtures compartidos (mocks)
├── test_produccion_service.py           # Tests de ProduccionService
├── test_ingresos_insumos_service.py     # Tests de IngresoProductoService
└── test_movimiento_insumos_service.py   # Tests de MovimientoInsumoService
```

## 🎯 Cobertura de Tests

### ProduccionService (test_produccion_service.py)

**Validación de Stock:**
- ✅ Validar con stock suficiente
- ✅ Validar con stock insuficiente
- ✅ Validar receta no encontrada
- ✅ Ignorar insumos opcionales

**Ejecución de Producción:**
- ✅ Ejecutar producción exitosa
- ✅ Ejecutar sin stock (debe fallar)
- ✅ Rollback en caso de error

**Historial y Trazabilidad:**
- ✅ Obtener historial de producciones
- ✅ Obtener trazabilidad completa
- ✅ Trazabilidad de producción inexistente

### IngresoProductoService (test_ingresos_insumos_service.py)

**CRUD:**
- ✅ Obtener todos los ingresos
- ✅ Obtener por ID (existente/no encontrado)
- ✅ Crear ingreso
- ✅ Actualizar ingreso (existente/no encontrado)
- ✅ Eliminar ingreso (existente/no encontrado)

**Lotes FEFO:**
- ✅ Obtener lotes FEFO de insumo
- ✅ Insumo no encontrado
- ✅ Obtener lotes con totales y proveedor
- ✅ Lotes sin stock

### MovimientoInsumoService (test_movimiento_insumos_service.py)

**CRUD:**
- ✅ Obtener todos los movimientos
- ✅ Lista vacía
- ✅ Obtener por ID (existente/no encontrado)
- ✅ Crear movimiento
- ✅ Crear múltiples movimientos

**Verificación:**
- ✅ Inicialización del repositorio
- ✅ Implementación de interfaz

## 🔍 Fixtures Disponibles (conftest.py)

### Mocks de Base de Datos
- `mock_db_session`: Sesión de DB mockeada

### Mocks de Datos
- `mock_receta_data`: Receta con insumos
- `mock_lotes_fefo`: Lotes FEFO
- `mock_produccion_creada`: Producción creada
- `mock_insumo`: Insumo mockeado
- `mock_ingreso`: Ingreso mockeado
- `mock_movimiento`: Movimiento mockeado
- `mock_historial_producciones`: Historial
- `mock_trazabilidad_produccion`: Trazabilidad completa

## ✅ Ventajas de estos Tests

1. **Rápidos**: No requieren base de datos real
2. **Independientes**: Cada test es aislado
3. **Repetibles**: Siempre dan el mismo resultado
4. **Enfocados**: Prueban solo la lógica de negocio
5. **Mantenibles**: Fáciles de actualizar

## 🐛 Debug de Tests

Para ver más detalles durante la ejecución:

```bash
# Ver prints y logs
pytest modules/gestion_almacen_inusmos/tests/ -v -s

# Detener en el primer error
pytest modules/gestion_almacen_inusmos/tests/ -v -x

# Ver traceback completo
pytest modules/gestion_almacen_inusmos/tests/ -v --tb=long
```

## 📝 Agregar Nuevos Tests

1. Crea fixtures en `conftest.py` si necesitas datos mock reutilizables
2. Usa `@patch` para mockear métodos del repositorio
3. Sigue el patrón AAA (Arrange, Act, Assert)
4. Documenta el escenario y resultado esperado

### Ejemplo:

```python
def test_mi_nuevo_caso(self, mock_db_session, mock_receta_data):
    """
    Test: Descripción del caso de prueba.
    
    Escenario:
    - Condiciones iniciales
    
    Resultado esperado:
    - Comportamiento esperado
    """
    # Arrange
    with patch.object(self.service.repository, 'metodo') as mock_metodo:
        mock_metodo.return_value = valor_esperado
        
        # Act
        resultado = self.service.metodo_a_probar(...)
        
        # Assert
        assert resultado == valor_esperado
        mock_metodo.assert_called_once()
```

## 🎓 Recursos

- [Documentación de pytest](https://docs.pytest.org/)
- [Documentación de unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
