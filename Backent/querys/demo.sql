-- =================================================================
-- DEMO: Panadería - Datos de prueba para endpoints FEFO y Producción
-- =================================================================
-- Este archivo es solo para referencia y pruebas manuales.
-- NO se inserta automáticamente en la base de datos.
-- =================================================================

-- Asegúrate de tener un usuario creado primero (para las FK)
-- Si no tienes usuario, créalo primero:
INSERT INTO usuario (nombre, apellidos, email, password) 
VALUES ('Admin', 'Panadería', 'admin@panaderia.com', 'hash_password_aqui')
ON CONFLICT (email) DO NOTHING;

-- Obtener el ID del usuario (para usar en los siguientes INSERTs)
-- En PostgreSQL puedes usar: SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com';

-- =================================================================
-- 1. PROVEEDORES
-- =================================================================

INSERT INTO proveedores (nombre, ruc_dni, numero_contacto, email_contacto, direccion_fiscal) VALUES
('Distribuidora Harinas del Sur', '20123456789', '987654321', 'ventas@harinassur.com', 'Av. Industrial 123, Lima'),
('Lácteos Gloria', '20987654321', '912345678', 'pedidos@gloria.com', 'Av. República de Panamá 456, Lima'),
('Huevos Don Pepe', '10456789012', '956789012', 'ventas@huevosdonpepe.com', 'Jr. Comercio 789, Lima');

-- =================================================================
-- 2. INSUMOS (Ingredientes para panadería)
-- =================================================================

INSERT INTO insumo (codigo, nombre, descripcion, unidad_medida, stock_minimo, perecible, categoria) VALUES
-- Harinas y derivados
('INS-001', 'Harina de Trigo', 'Harina de trigo todo uso para panadería', 'KILOGRAMO', 50.0000, false, 'HARINAS'),
('INS-002', 'Levadura Seca', 'Levadura instantánea para pan', 'KILOGRAMO', 5.0000, true, 'LEVADURAS'),
('INS-003', 'Sal de Mesa', 'Sal refinada para cocina', 'KILOGRAMO', 10.0000, false, 'CONDIMENTOS'),

-- Lácteos
('INS-004', 'Leche Fresca', 'Leche entera pasteurizada', 'LITRO', 20.0000, true, 'LACTEOS'),
('INS-005', 'Mantequilla', 'Mantequilla sin sal', 'KILOGRAMO', 10.0000, true, 'LACTEOS'),
('INS-006', 'Huevos', 'Huevos frescos de gallina', 'UNIDAD', 100.0000, true, 'HUEVOS'),

-- Azúcares y endulzantes
('INS-007', 'Azúcar Blanca', 'Azúcar refinada', 'KILOGRAMO', 30.0000, false, 'AZUCARES'),
('INS-008', 'Azúcar Impalpable', 'Azúcar en polvo para decoración', 'KILOGRAMO', 5.0000, false, 'AZUCARES'),

-- Otros
('INS-009', 'Aceite Vegetal', 'Aceite de soya refinado', 'LITRO', 15.0000, false, 'ACEITES'),
('INS-010', 'Esencia de Vainilla', 'Extracto puro de vainilla', 'LITRO', 2.0000, false, 'ESENCIAS');

-- =================================================================
-- 3. PRODUCTOS TERMINADOS
-- =================================================================

INSERT INTO productos_terminados (codigo_producto, nombre, descripcion, unidad_medida, stock_actual, stock_minimo, vida_util_dias, precio_venta) VALUES
('PROD-001', 'Pan Francés', 'Pan francés crujiente tradicional', 'UNIDAD', 0, 50, 1, 0.30),
('PROD-002', 'Bizcocho de Vainilla', 'Bizcocho esponjoso sabor vainilla', 'UNIDAD', 0, 10, 3, 25.00);

-- =================================================================
-- 4. RECETAS
-- =================================================================

-- Obtener IDs de productos (ajustar según tu base de datos)
-- SELECT id_producto FROM productos_terminados WHERE codigo_producto = 'PROD-001'; -- Pan Francés
-- SELECT id_producto FROM productos_terminados WHERE codigo_producto = 'PROD-002'; -- Bizcocho

-- RECETA 1: Pan Francés (rinde 20 unidades)
INSERT INTO recetas (id_producto, codigo_receta, nombre_receta, descripcion, rendimiento_producto_terminado, costo_estimado, estado) VALUES
((SELECT id_producto FROM productos_terminados WHERE codigo_producto = 'PROD-001'),
 'REC-001', 'Pan Francés Clásico', 'Receta tradicional de pan francés crujiente', 20.0000, 5.00, 'ACTIVA');

-- RECETA 2: Bizcocho de Vainilla (rinde 1 bizcocho)
INSERT INTO recetas (id_producto, codigo_receta, nombre_receta, descripcion, rendimiento_producto_terminado, costo_estimado, estado) VALUES
((SELECT id_producto FROM productos_terminados WHERE codigo_producto = 'PROD-002'),
 'REC-002', 'Bizcocho de Vainilla', 'Bizcocho esponjoso con esencia de vainilla', 1.0000, 15.00, 'ACTIVA');

-- =================================================================
-- 5. DETALLE DE RECETAS (Ingredientes por receta)
-- =================================================================

-- Detalle RECETA 1: Pan Francés (para 20 unidades)
INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones) VALUES
-- Harina: 1 kg para 20 panes
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-001'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-001'), 1.0000, 3.50, false, 'Harina todo uso'),
-- Levadura: 0.02 kg (20g) para 20 panes
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-001'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-002'), 0.0200, 25.00, false, 'Levadura instantánea'),
-- Sal: 0.02 kg (20g) para 20 panes
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-001'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-003'), 0.0200, 1.50, false, 'Sal fina'),
-- Agua: No está en insumos, se asume disponible
-- Aceite: 0.05 L (50ml) para 20 panes
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-001'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-009'), 0.0500, 8.00, true, 'Opcional para la masa');

-- Detalle RECETA 2: Bizcocho de Vainilla (para 1 bizcocho)
INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones) VALUES
-- Harina: 0.3 kg (300g)
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-001'), 0.3000, 3.50, false, 'Harina tamizada'),
-- Azúcar: 0.25 kg (250g)
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-007'), 0.2500, 4.00, false, 'Azúcar blanca'),
-- Huevos: 4 unidades
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-006'), 4.0000, 0.50, false, '4 huevos grandes'),
-- Mantequilla: 0.15 kg (150g)
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-005'), 0.1500, 18.00, false, 'Mantequilla derretida'),
-- Leche: 0.2 L (200ml)
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-004'), 0.2000, 5.00, false, 'Leche a temperatura ambiente'),
-- Esencia de Vainilla: 0.01 L (10ml)
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-010'), 0.0100, 80.00, false, 'Esencia pura'),
-- Levadura: 0.01 kg (10g) - polvo de hornear
((SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-002'), 0.0100, 25.00, false, 'Polvo de hornear');

-- =================================================================
-- 6. INGRESOS DE INSUMOS (Lotes para probar FEFO)
-- =================================================================

-- Primero obtener IDs necesarios
-- SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com';
-- SELECT id_proveedor FROM proveedores WHERE ruc_dni = '20123456789'; -- Harinas del Sur

-- INGRESO 1: Compra de Harinas (Lote con vencimiento lejano)
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total) VALUES
('ING-2025-001', 'F001-00123', 'FACTURA', '2025-11-20 10:00:00', '2025-11-20', 
 (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'),
 (SELECT id_proveedor FROM proveedores WHERE ruc_dni = '20123456789'),
 'Compra inicial de harinas', 'COMPLETADO', 350.00);

-- Detalle del INGRESO 1 (Lotes)
INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante) VALUES
-- Harina - Lote 1 (vence en 6 meses)
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-001'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-001'), 50.0000, 3.50, 175.00, '2026-05-20', 50.0000),
-- Levadura - Lote 1 (vence en 3 meses)
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-001'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-002'), 5.0000, 25.00, 125.00, '2026-02-20', 5.0000),
-- Sal - Lote 1 (vence en 2 años)
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-001'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-003'), 20.0000, 1.50, 30.00, '2027-11-20', 20.0000);

-- INGRESO 2: Compra de Lácteos (Lotes con vencimiento próximo - FEFO)
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total) VALUES
('ING-2025-002', 'F001-00456', 'FACTURA', '2025-11-22 09:00:00', '2025-11-22', 
 (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'),
 (SELECT id_proveedor FROM proveedores WHERE ruc_dni = '20987654321'),
 'Compra de lácteos frescos', 'COMPLETADO', 280.00);

-- Detalle del INGRESO 2 (Lotes - productos perecederos)
INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante) VALUES
-- Leche - Lote 1 (vence en 7 días - PRIORITARIO FEFO)
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-002'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-004'), 20.0000, 5.00, 100.00, '2025-12-03', 20.0000),
-- Mantequilla - Lote 1 (vence en 30 días)
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-002'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-005'), 10.0000, 18.00, 180.00, '2025-12-26', 10.0000);

-- INGRESO 3: Compra de Huevos (Lotes múltiples para probar FEFO)
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total) VALUES
('ING-2025-003', 'F001-00789', 'FACTURA', '2025-11-15 08:00:00', '2025-11-15', 
 (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'),
 (SELECT id_proveedor FROM proveedores WHERE ruc_dni = '10456789012'),
 'Compra de huevos - Lote antiguo', 'COMPLETADO', 75.00);

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante) VALUES
-- Huevos - Lote 1 (vence en 5 días - MÁS PRIORITARIO)
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-003'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-006'), 150.0000, 0.50, 75.00, '2025-12-01', 150.0000);

-- INGRESO 4: Segunda compra de Huevos (Lote más nuevo)
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total) VALUES
('ING-2025-004', 'F001-00890', 'FACTURA', '2025-11-25 08:00:00', '2025-11-25', 
 (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'),
 (SELECT id_proveedor FROM proveedores WHERE ruc_dni = '10456789012'),
 'Compra de huevos - Lote nuevo', 'COMPLETADO', 100.00);

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante) VALUES
-- Huevos - Lote 2 (vence en 15 días - MENOS PRIORITARIO)
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-004'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-006'), 200.0000, 0.50, 100.00, '2025-12-11', 200.0000);

-- INGRESO 5: Compra de Azúcares y Esencias
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total) VALUES
('ING-2025-005', 'F001-00999', 'FACTURA', '2025-11-18 11:00:00', '2025-11-18', 
 (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'),
 (SELECT id_proveedor FROM proveedores WHERE ruc_dni = '20123456789'),
 'Compra de azúcares y esencias', 'COMPLETADO', 380.00);

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante) VALUES
-- Azúcar Blanca (sin vencimiento próximo)
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-005'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-007'), 50.0000, 4.00, 200.00, '2027-11-18', 50.0000),
-- Azúcar Impalpable
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-005'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-008'), 10.0000, 6.00, 60.00, '2027-11-18', 10.0000),
-- Aceite Vegetal
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-005'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-009'), 10.0000, 8.00, 80.00, '2027-11-18', 10.0000),
-- Esencia de Vainilla
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-005'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-010'), 0.5000, 80.00, 40.00, '2027-11-18', 0.5000);

-- INGRESO 6: Compra adicional de Harina (Lote con vencimiento próximo para probar FEFO)
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total) VALUES
('ING-2025-006', 'F001-01000', 'FACTURA', '2025-11-27 12:00:00', '2025-11-27', 
 (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'),
 (SELECT id_proveedor FROM proveedores WHERE ruc_dni = '20123456789'),
 'Compra adicional de harina - vence pronto', 'COMPLETADO', 140.00);

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante) VALUES
-- Harina - Lote 2 (vence en 1 mes - PRIORITARIO FEFO)
((SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = 'ING-2025-006'),
 (SELECT id_insumo FROM insumo WHERE codigo = 'INS-001'), 40.0000, 3.50, 140.00, '2025-12-27', 40.0000);

-- =================================================================
-- 8. PRODUCCIONES DE EJEMPLO
-- =================================================================

-- Producción de ejemplo para probar trazabilidad e historial
INSERT INTO produccion (numero_produccion, id_receta, cantidad_batch, id_user, fecha_produccion, observaciones, anulado) VALUES
('PROD-202511-1', (SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-001'), 1, (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'), '2025-11-28 10:00:00', 'Producción de ejemplo - 20 panes', false),
('PROD-202511-2', (SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002'), 2, (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'), '2025-11-28 14:00:00', 'Producción de ejemplo - 2 bizcochos', false);

-- =================================================================
-- 9. VENTAS DE EJEMPLO
-- =================================================================

-- VENTA 1: Venta de panes (día actual)
INSERT INTO ventas (numero_venta, fecha_venta, total, metodo_pago, id_user, observaciones, anulado) VALUES
('VENTA-202511-1', '2025-11-29 09:30:00', 6.00, 'efectivo', (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'), 'Venta de mostrador - 20 panes', false);

-- Detalle de VENTA 1
INSERT INTO venta_detalles (id_venta, id_producto, cantidad, precio_unitario, descuento_porcentaje, subtotal) VALUES
((SELECT id_venta FROM ventas WHERE numero_venta = 'VENTA-202511-1'),
 (SELECT id_producto FROM productos_terminados WHERE codigo_producto = 'PROD-001'), 20, 0.30, 0, 6.00);

-- VENTA 2: Venta de bizcochos con descuento
INSERT INTO ventas (numero_venta, fecha_venta, total, metodo_pago, id_user, observaciones, anulado) VALUES
('VENTA-202511-2', '2025-11-29 11:00:00', 17.50, 'tarjeta', (SELECT id_user FROM usuario WHERE email = 'admin@panaderia.com'), 'Venta con descuento del 30% por antigüedad', false);

-- Detalle de VENTA 2 (1 bizcocho con 30% descuento)
INSERT INTO venta_detalles (id_venta, id_producto, cantidad, precio_unitario, descuento_porcentaje, subtotal) VALUES
((SELECT id_venta FROM ventas WHERE numero_venta = 'VENTA-202511-2'),
 (SELECT id_producto FROM productos_terminados WHERE codigo_producto = 'PROD-002'), 1, 25.00, 30, 17.50);

-- =================================================================
-- 7. CONSULTAS DE PRUEBA PARA LOS ENDPOINTS
-- =================================================================

-- ===== PRUEBA ENDPOINT: GET /ingresos_productos/lotes-fefo-total/{id_insumo} =====
-- Probar con el insumo de Huevos (tiene 2 lotes con diferentes fechas de vencimiento)
-- SELECT id_insumo FROM insumo WHERE codigo = 'INS-006';
-- Usar ese ID en: GET /api/v1/ingresos_productos/lotes-fefo-total/{id_insumo}
-- Esperado: Debe mostrar 2 lotes ordenados por FEFO (primero el que vence 2025-12-01)

-- ===== PRUEBA ENDPOINT: POST /produccion/validar-stock =====
-- Validar stock para producir 40 panes (2 batches de la receta REC-001)
-- SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-001';
-- Usar: POST /api/v1/produccion/validar-stock?id_receta={id}&cantidad_batch=2
-- Esperado: Debe retornar que SÍ hay stock suficiente

-- ===== PRUEBA ENDPOINT: POST /produccion/ejecutar =====
-- Ejecutar producción de 5 bizcochos (5 batches de la receta REC-002)
-- SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002';
-- Body JSON:
-- {
--   "id_receta": {id_receta},
--   "cantidad_batch": 5,
--   "id_user": {id_user},
--   "observaciones": "Producción de prueba - 5 bizcochos"
-- }
-- Esperado: 
-- - Debe descontar de los lotes FEFO
-- - Huevos: primero del lote que vence 2025-12-01, luego del que vence 2025-12-11
-- - Crear movimientos de SALIDA en movimiento_insumos

-- ===== VERIFICAR RESULTADO DE PRODUCCIÓN =====
-- Después de ejecutar producción, verificar:

-- 1. Stock actualizado de lotes:
-- SELECT 
--     i.nombre, 
--     iid.id_ingreso_detalle,
--     iid.cantidad_ingresada,
--     iid.cantidad_restante,
--     iid.fecha_vencimiento
-- FROM ingresos_insumos_detalle iid
-- JOIN insumo i ON iid.id_insumo = i.id_insumo
-- WHERE i.codigo IN ('INS-006', 'INS-001', 'INS-007')
-- ORDER BY i.nombre, iid.fecha_vencimiento;

-- 2. Movimientos de salida creados:
-- SELECT 
--     mi.numero_movimiento,
--     i.nombre AS insumo,
--     mi.tipo_movimiento,
--     mi.motivo,
--     mi.cantidad,
--     mi.stock_anterior_lote,
--     mi.stock_nuevo_lote,
--     mi.observaciones
-- FROM movimiento_insumos mi
-- JOIN insumo i ON mi.id_insumo = i.id_insumo
-- WHERE mi.tipo_documento_origen = 'PRODUCCION'
-- ORDER BY mi.fecha_movimiento DESC;

-- ===== PRUEBAS DE CASOS DE BORDE =====

-- ===== Prueba de Stock Insuficiente =====
-- Intentar ejecutar producción de 100 bizcochos (excede stock de huevos)
-- SELECT id_receta FROM recetas WHERE codigo_receta = 'REC-002';
-- Body JSON:
-- {
--   "id_receta": {id_receta},
--   "cantidad_batch": 100,
--   "id_user": {id_user},
--   "observaciones": "Prueba stock insuficiente"
-- }
-- Esperado: Error de validación, stock intacto

-- ===== Prueba de Rollback de Transacción =====
-- Para probar rollback, modificar temporalmente el código para forzar error
-- (ej. en service.py, agregar raise Exception después de descontar algunos insumos)
-- Ejecutar producción normal, verificar que si falla, stock se restaure
-- Verificar con queries de stock antes/después

-- ===== Verificar FEFO con múltiples lotes =====
-- Después de agregar el lote de harina nuevo (ING-2025-006), verificar que se use primero
-- SELECT id_insumo FROM insumo WHERE codigo = 'INS-001';
-- GET /api/v1/ingresos_productos/lotes-fefo-total/{id_insumo}
-- Esperado: Lote que vence 2025-12-27 primero, luego 2026-05-20

-- =================================================================
-- PRUEBAS PARA VENTAS (FC-02)
-- =================================================================

-- ===== PRUEBA ENDPOINT: GET /ventas/productos-disponibles =====
-- Obtener productos disponibles con descuentos sugeridos
-- GET /api/v1/ventas/productos-disponibles
-- Esperado: Lista de productos con stock > 0 y descuento según días de antigüedad

-- ===== PRUEBA ENDPOINT: POST /ventas/registrar =====
-- Registrar una venta de productos
-- Body JSON:
-- {
--   "items": [
--     {
--       "id_producto": {id_producto_pan},
--       "cantidad": 5,
--       "precio_unitario": 0.30,
--       "descuento_porcentaje": 0
--     }
--   ],
--   "metodo_pago": "efectivo",
--   "observaciones": "Venta de prueba"
-- }
-- Esperado: 
-- - Venta creada con número VENTA-YYYYMM-N
-- - Stock de productos_terminados descontado
-- - Movimiento de SALIDA creado en movimiento_productos_terminados

-- ===== PRUEBA ENDPOINT: GET /ventas/del-dia =====
-- Obtener ventas del día actual
-- GET /api/v1/ventas/del-dia
-- Esperado: Lista de ventas del día con total y cantidad de items

-- ===== PRUEBA ENDPOINT: GET /ventas/{id_venta} =====
-- Obtener detalle de una venta
-- SELECT id_venta FROM ventas WHERE numero_venta = 'VENTA-202511-1';
-- GET /api/v1/ventas/{id_venta}
-- Esperado: Detalle completo de la venta con todos sus items

-- ===== PRUEBA ENDPOINT: POST /ventas/{id_venta}/anular =====
-- Anular una venta y restaurar stock
-- POST /api/v1/ventas/{id_venta}/anular
-- Esperado:
-- - Venta marcada como anulada
-- - Stock de productos restaurado
-- - Movimiento de ENTRADA (compensación) creado

-- ===== VERIFICAR STOCK DESPUÉS DE VENTA =====
-- SELECT 
--     pt.codigo_producto,
--     pt.nombre,
--     pt.stock_actual
-- FROM productos_terminados pt
-- WHERE pt.codigo_producto IN ('PROD-001', 'PROD-002')
-- ORDER BY pt.codigo_producto;

-- ===== VERIFICAR MOVIMIENTOS DE PRODUCTOS =====
-- SELECT 
--     mpt.numero_movimiento,
--     pt.nombre AS producto,
--     mpt.tipo_movimiento,
--     mpt.motivo,
--     mpt.cantidad,
--     mpt.stock_anterior,
--     mpt.stock_nuevo,
--     mpt.fecha_movimiento
-- FROM movimiento_productos_terminados mpt
-- JOIN productos_terminados pt ON mpt.id_producto = pt.id_producto
-- WHERE mpt.tipo_documento_origen = 'VENTA'
-- ORDER BY mpt.fecha_movimiento DESC;

-- =================================================================
-- RESUMEN DE DATOS INSERTADOS
-- =================================================================
-- 
-- PROVEEDORES: 3
-- INSUMOS: 10
-- PRODUCTOS TERMINADOS: 2
-- RECETAS: 2
--   - Pan Francés (REC-001): 4 ingredientes, rinde 20 unidades
--   - Bizcocho de Vainilla (REC-002): 7 ingredientes, rinde 1 unidad
-- INGRESOS DE INSUMOS: 6 (con múltiples lotes)
-- LOTES TOTALES: 11
-- PRODUCCIONES DE EJEMPLO: 2
-- VENTAS DE EJEMPLO: 2
--
-- STOCK DISPONIBLE INICIAL:
-- - Harina: 90 kg (2 lotes: vence 2025-12-27 y 2026-05-20)
-- - Levadura: 5 kg (1 lote)
-- - Sal: 20 kg (1 lote, vence 2027-11-20)
-- - Leche: 20 L (1 lote, vence pronto)
-- - Mantequilla: 10 kg (1 lote)
-- - Huevos: 350 unidades (2 lotes, FEFO importante)
-- - Azúcar Blanca: 50 kg (1 lote)
-- - Azúcar Impalpable: 10 kg (1 lote)
-- - Aceite: 10 L (1 lote, vence 2027-11-18)
-- - Esencia Vainilla: 0.5 L (1 lote)
-- =================================================================
