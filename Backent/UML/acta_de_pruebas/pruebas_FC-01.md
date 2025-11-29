# Pruebas Manuales para FC-01: Salidas por Producción con Descuento Automático FEFO

## Descripción General
Este documento lista las pruebas manuales necesarias para verificar la funcionalidad de FC-01: Salidas por producción con descuento automático FEFO. Las pruebas se basan en los datos de `demo.sql` y utilizan los endpoints de la API de producción.

## Pruebas Requeridas

### 1. Validación de Stock
**Endpoint:** `POST /produccion/validar-stock`  
**Objetivo:** Verificar que la validación de stock funcione correctamente para una receta y cantidad de lotes.

- **Prueba 1.1:** Validar stock para 2 lotes de Pan Francés (REC-001).
  - Parámetros: `id_receta` (Pan Francés), `cantidad_batch=2`
  - Resultado esperado: Stock suficiente para todos los insumos (harina, levadura, sal, aceite).
  
- **Prueba 1.2:** Validar stock para 5 lotes de Bizcocho de Vainilla (REC-002).
  - Parámetros: `id_receta` (Bizcocho), `cantidad_batch=5`
  - Resultado esperado: Stock suficiente para todos los insumos (harina, azúcar, huevos, mantequilla, leche, vainilla, levadura).

### 2. Ejecución de Producción con FEFO
**Endpoint:** `POST /produccion/ejecutar`  
**Objetivo:** Verificar que la producción descuente insumos siguiendo FEFO (primero los lotes que vencen primero).

- **Prueba 2.1:** Ejecutar producción de 5 bizcochos (REC-002).
  - Parámetros: `id_receta` (Bizcocho), `cantidad_batch=5`, `id_user` (usuario admin), `observaciones="Prueba FEFO"`
  - Resultado esperado: 
    - Huevos descontados primero del lote que vence el 2025-12-01 (150 unidades disponibles), luego del lote 2025-12-11.
    - Movimientos de salida creados en `movimiento_insumos`.
    - Stock de productos terminados incrementado.
    - Registro de producción creado.

- **Prueba 2.2:** Ejecutar producción de 2 lotes de Pan Francés (REC-001).
  - Parámetros: `id_receta` (Pan Francés), `cantidad_batch=2`, `id_user` (usuario admin), `observaciones="Prueba Pan"`
  - Resultado esperado: 
    - Insumos descontados siguiendo FEFO (priorizando lotes con vencimiento próximo).
    - Movimientos correctos y stock actualizado.

### 3. Trazabilidad de Producción
**Endpoint:** `GET /produccion/{id}/trazabilidad`  
**Objetivo:** Verificar que se pueda rastrear qué lotes se consumieron en una producción.

- **Prueba 3.1:** Obtener trazabilidad de la producción creada en Prueba 2.1.
  - Parámetros: `id` (ID de la producción de bizcochos)
  - Resultado esperado: Detalle de lotes consumidos, cantidades, fechas de vencimiento, ordenados por FEFO.

- **Prueba 3.2:** Obtener trazabilidad de la producción creada en Prueba 2.2.
  - Parámetros: `id` (ID de la producción de pan)
  - Resultado esperado: Información completa de insumos usados.

### 4. Historial de Producciones
**Endpoint:** `GET /produccion/historial`  
**Objetivo:** Verificar que el historial de producciones se muestre correctamente.

- **Prueba 4.1:** Obtener historial de producciones.
  - Parámetros: Paginación por defecto
  - Resultado esperado: Lista de producciones ejecutadas, incluyendo las de las pruebas anteriores.

### 5. Casos de Borde
**Objetivo:** Verificar comportamiento en situaciones excepcionales.

- **Prueba 5.1:** Intento de producción con stock insuficiente.
  - Ejecutar producción de 100 bizcochos (excede stock disponible).
  - Resultado esperado: Error de validación, transacción no ejecutada, stock intacto.

- **Prueba 5.2:** Simular rollback de transacción.
  - Intentar producción que cause error interno (ej. modificar temporalmente el código para forzar error).
  - Resultado esperado: Ningún cambio en stock o movimientos si falla.

## Notas Adicionales
- Todas las pruebas usan los datos de `demo.sql`.
- Verificar consultas SQL en `demo.sql` para inspeccionar cambios en lotes y movimientos antes/después de cada prueba.
- Las pruebas son manuales: ejecutar endpoints via Postman o similar, luego verificar base de datos.