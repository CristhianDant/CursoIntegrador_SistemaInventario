# Pruebas Manuales para FC-02: Ventas con Descuento Automático de Stock

## Descripción General
Este documento lista las pruebas manuales necesarias para verificar la funcionalidad de FC-02: Sistema de ventas con descuento automático de stock de productos terminados. Las pruebas se basan en los datos de `demo.sql` y utilizan los endpoints de la API de ventas.

## Pruebas Requeridas

### 1. Listar Productos Disponibles para Venta
**Endpoint:** `GET /ventas/productos-disponibles`  
**Objetivo:** Verificar que se listen correctamente los productos con stock disponible y descuentos sugeridos según antigüedad (FC-09).

- **Prueba 1.1:** Obtener productos disponibles.
  - Parámetros: Ninguno
  - Resultado esperado: 
    - Lista de productos con `stock_actual > 0`
    - Campo `dias_desde_produccion` calculado correctamente
    - Campo `descuento_sugerido`:
      - 30% si tiene 1 día de antigüedad
      - 50% si tiene 2 días de antigüedad
      - 70% si tiene 3+ días de antigüedad
      - 0% si es del día o sin producción

### 2. Registrar Venta Simple
**Endpoint:** `POST /ventas/registrar`  
**Objetivo:** Verificar que la venta se registre correctamente y descuente stock automáticamente.

- **Prueba 2.1:** Registrar venta de 5 panes.
  - Body JSON:
    ```json
    {
      "items": [
        {
          "id_producto": 1,
          "cantidad": 5,
          "precio_unitario": 0.30,
          "descuento_porcentaje": 0
        }
      ],
      "metodo_pago": "efectivo",
      "observaciones": "Venta de prueba"
    }
    ```
  - Resultado esperado:
    - Venta creada con número `VENTA-YYYYMM-N`
    - Total calculado correctamente: `5 × 0.30 = 1.50`
    - Stock de Pan Francés descontado en 5 unidades
    - Movimiento de SALIDA creado en `movimiento_productos_terminados`
    - `tipo_movimiento = SALIDA`, `motivo = VENTA`

- **Prueba 2.2:** Registrar venta con descuento.
  - Body JSON:
    ```json
    {
      "items": [
        {
          "id_producto": 2,
          "cantidad": 1,
          "precio_unitario": 25.00,
          "descuento_porcentaje": 30
        }
      ],
      "metodo_pago": "tarjeta",
      "observaciones": "Venta con descuento por antigüedad"
    }
    ```
  - Resultado esperado:
    - Total calculado: `25.00 × 0.70 = 17.50` (30% descuento)
    - Stock de Bizcocho descontado en 1 unidad

### 3. Obtener Detalle de Venta
**Endpoint:** `GET /ventas/{id_venta}`  
**Objetivo:** Verificar que se pueda consultar el detalle completo de una venta.

- **Prueba 3.1:** Obtener detalle de venta creada en Prueba 2.1.
  - Parámetros: `id_venta` (ID de la venta de panes)
  - Resultado esperado:
    - Información completa de la venta
    - Lista de detalles con productos, cantidades y precios
    - Subtotales correctos

### 4. Listar Ventas del Día
**Endpoint:** `GET /ventas/del-dia`  
**Objetivo:** Verificar que se listen correctamente las ventas del día actual.

- **Prueba 4.1:** Obtener ventas del día actual.
  - Parámetros: Sin fecha (usa fecha actual)
  - Resultado esperado:
    - Lista de ventas del día
    - Total de ventas (cantidad)
    - Monto total vendido (suma de totales no anulados)

- **Prueba 4.2:** Obtener ventas de una fecha específica.
  - Query param: `fecha=2025-11-29`
  - Resultado esperado:
    - Ventas de esa fecha específica

### 5. Anular Venta y Restaurar Stock
**Endpoint:** `POST /ventas/{id_venta}/anular`  
**Objetivo:** Verificar que al anular una venta se restaure el stock correctamente.

- **Prueba 5.1:** Anular venta de la Prueba 2.1.
  - Parámetros: `id_venta` (ID de la venta de panes)
  - Resultado esperado:
    - Campo `anulado = true` en la venta
    - Stock de Pan Francés restaurado (+5 unidades)
    - Movimiento de ENTRADA creado en `movimiento_productos_terminados`
    - `tipo_movimiento = ENTRADA`, `motivo = ANULACION_VENTA`

### 6. Validaciones y Casos de Borde
**Objetivo:** Verificar que las validaciones funcionen correctamente.

- **Prueba 6.1:** Intento de venta con stock insuficiente.
  - Intentar vender 100 bizcochos (excede stock disponible)
  - Resultado esperado:
    - Error 400 con mensaje "Stock insuficiente para..."
    - Stock intacto (no se descuenta)
    - No se crea venta ni movimientos

- **Prueba 6.2:** Intento de anular venta ya anulada.
  - Intentar anular la misma venta dos veces
  - Resultado esperado:
    - Error 400 con mensaje "La venta ya está anulada"
    - Stock no se modifica

- **Prueba 6.3:** Método de pago inválido.
  - Enviar método de pago no válido (ej. "cheque")
  - Resultado esperado:
    - Error 422 de validación

### 7. Verificación de Integridad
**Objetivo:** Verificar que los datos se registren correctamente en la base de datos.

- **Prueba 7.1:** Verificar stock de productos después de ventas.
  - Query SQL:
    ```sql
    SELECT codigo_producto, nombre, stock_actual
    FROM productos_terminados
    WHERE codigo_producto IN ('PROD-001', 'PROD-002')
    ORDER BY codigo_producto;
    ```
  - Resultado esperado: Stock actualizado según ventas realizadas

- **Prueba 7.2:** Verificar movimientos de productos terminados.
  - Query SQL:
    ```sql
    SELECT 
        mpt.numero_movimiento,
        pt.nombre AS producto,
        mpt.tipo_movimiento,
        mpt.motivo,
        mpt.cantidad,
        mpt.stock_anterior,
        mpt.stock_nuevo,
        mpt.fecha_movimiento
    FROM movimiento_productos_terminados mpt
    JOIN productos_terminados pt ON mpt.id_producto = pt.id_producto
    WHERE mpt.tipo_documento_origen = 'VENTA'
    ORDER BY mpt.fecha_movimiento DESC;
    ```
  - Resultado esperado: Movimientos de SALIDA y ENTRADA (anulaciones) correctos

- **Prueba 7.3:** Verificar consistencia de totales.
  - Sumar `subtotal` de `venta_detalles` debe igual `total` en `ventas`
  - Query SQL:
    ```sql
    SELECT 
        v.numero_venta,
        v.total AS total_venta,
        SUM(vd.subtotal) AS suma_detalles
    FROM ventas v
    LEFT JOIN venta_detalles vd ON v.id_venta = vd.id_venta
    GROUP BY v.id_venta, v.numero_venta, v.total
    HAVING v.total <> SUM(vd.subtotal);
    ```
  - Resultado esperado: Sin resultados (totales consistentes)

## Notas Adicionales
- Todas las pruebas usan los datos de `demo.sql`.
- Las pruebas son manuales: ejecutar endpoints via Postman, Thunder Client o similar.
- Verificar base de datos con las queries SQL proporcionadas.
- El descuento sugerido (FC-09) se calcula basado en la fecha de última producción del producto.
