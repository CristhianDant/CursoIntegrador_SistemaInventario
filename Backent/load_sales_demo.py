"""
Script para cargar datos de demo específicos para probar el Punto de Venta.
Ejecutar desde el directorio Backent con el entorno virtual activo:
    python load_sales_demo.py
"""

from sqlalchemy import text
from database import engine
from datetime import datetime, date, timedelta

# SQL para datos de prueba de ventas
SALES_DEMO_SQL = """
-- =================================================================
-- DEMO: Datos de prueba para PUNTO DE VENTA y ALERTAS
-- =================================================================

-- Actualizar stock de productos terminados para tener productos disponibles
UPDATE productos_terminados SET stock_actual = 100, precio_venta = 0.30 WHERE codigo_producto = 'PROD-001';
UPDATE productos_terminados SET stock_actual = 20, precio_venta = 25.00 WHERE codigo_producto = 'PROD-002';

-- Agregar más productos terminados para pruebas de ventas
INSERT INTO productos_terminados (codigo_producto, nombre, descripcion, unidad_medida, stock_actual, stock_minimo, vida_util_dias, precio_venta) VALUES
('PROD-003', 'Croissant', 'Croissant de mantequilla tradicional', 'UNIDAD', 50, 20, 2, 3.50),
('PROD-004', 'Empanada de Pollo', 'Empanada rellena de pollo', 'UNIDAD', 30, 15, 1, 4.00),
('PROD-005', 'Torta de Chocolate', 'Torta de chocolate con ganache', 'UNIDAD', 5, 3, 4, 45.00),
('PROD-006', 'Galletas de Avena', 'Paquete de 6 galletas de avena', 'PAQUETE', 40, 20, 7, 8.00),
('PROD-007', 'Pan Integral', 'Pan integral con semillas', 'UNIDAD', 60, 30, 2, 1.50),
('PROD-008', 'Alfajor de Maicena', 'Alfajor relleno de manjar', 'UNIDAD', 80, 40, 5, 2.50),
('PROD-009', 'Pie de Manzana', 'Pie de manzana individual', 'UNIDAD', 15, 5, 3, 12.00),
('PROD-010', 'Rosquita Dulce', 'Rosquita con azúcar glass', 'UNIDAD', 100, 50, 2, 0.50)
ON CONFLICT (codigo_producto) DO UPDATE SET 
    stock_actual = EXCLUDED.stock_actual,
    precio_venta = EXCLUDED.precio_venta;

-- Crear productos del día anterior (para probar descuentos automáticos)
INSERT INTO productos_terminados (codigo_producto, nombre, descripcion, unidad_medida, stock_actual, stock_minimo, vida_util_dias, precio_venta, fecha_produccion) VALUES
('PROD-011', 'Pan de Ayer', 'Pan del día anterior con descuento', 'UNIDAD', 25, 10, 1, 0.30, CURRENT_DATE - INTERVAL '1 day'),
('PROD-012', 'Bizcocho de Ayer', 'Bizcocho del día anterior', 'UNIDAD', 8, 3, 3, 25.00, CURRENT_DATE - INTERVAL '1 day'),
('PROD-013', 'Croissant de Ayer', 'Croissant del día anterior', 'UNIDAD', 12, 5, 2, 3.50, CURRENT_DATE - INTERVAL '2 days')
ON CONFLICT (codigo_producto) DO UPDATE SET 
    stock_actual = EXCLUDED.stock_actual,
    fecha_produccion = EXCLUDED.fecha_produccion;

-- =================================================================
-- DATOS PARA ALERTAS Y SEMÁFORO
-- =================================================================

-- Crear insumos con vencimiento próximo para alertas
INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT 
    (SELECT id_ingreso FROM ingresos_insumos ORDER BY id_ingreso LIMIT 1),
    i.id_insumo, 
    10.0000, 
    5.00, 
    50.00, 
    CURRENT_DATE + INTERVAL '2 days',  -- Vence en 2 días (ROJO)
    10.0000
FROM insumo i WHERE i.codigo = 'INS-004' AND NOT EXISTS (
    SELECT 1 FROM ingresos_insumos_detalle iid 
    JOIN ingresos_insumos ii ON iid.id_ingreso = ii.id_ingreso
    WHERE iid.id_insumo = i.id_insumo AND iid.fecha_vencimiento = CURRENT_DATE + INTERVAL '2 days'
);

-- Insertar lote de leche que vence en 5 días (ROJO)
INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT 
    (SELECT id_ingreso FROM ingresos_insumos ORDER BY id_ingreso LIMIT 1),
    i.id_insumo, 
    15.0000, 
    5.00, 
    75.00, 
    CURRENT_DATE + INTERVAL '5 days',
    15.0000
FROM insumo i WHERE i.codigo = 'INS-004' AND NOT EXISTS (
    SELECT 1 FROM ingresos_insumos_detalle iid 
    JOIN ingresos_insumos ii ON iid.id_ingreso = ii.id_ingreso
    WHERE iid.id_insumo = i.id_insumo AND iid.fecha_vencimiento = CURRENT_DATE + INTERVAL '5 days'
);

-- Insertar lote de mantequilla que vence en 10 días (AMARILLO)
INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT 
    (SELECT id_ingreso FROM ingresos_insumos ORDER BY id_ingreso LIMIT 1),
    i.id_insumo, 
    5.0000, 
    18.00, 
    90.00, 
    CURRENT_DATE + INTERVAL '10 days',
    5.0000
FROM insumo i WHERE i.codigo = 'INS-005' AND NOT EXISTS (
    SELECT 1 FROM ingresos_insumos_detalle iid 
    JOIN ingresos_insumos ii ON iid.id_ingreso = ii.id_ingreso
    WHERE iid.id_insumo = i.id_insumo AND iid.fecha_vencimiento = CURRENT_DATE + INTERVAL '10 days'
);

-- Insertar lote de huevos que vence en 8 días (AMARILLO)
INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT 
    (SELECT id_ingreso FROM ingresos_insumos ORDER BY id_ingreso LIMIT 1),
    i.id_insumo, 
    100.0000, 
    0.50, 
    50.00, 
    CURRENT_DATE + INTERVAL '8 days',
    100.0000
FROM insumo i WHERE i.codigo = 'INS-006' AND NOT EXISTS (
    SELECT 1 FROM ingresos_insumos_detalle iid 
    JOIN ingresos_insumos ii ON iid.id_ingreso = ii.id_ingreso
    WHERE iid.id_insumo = i.id_insumo AND iid.fecha_vencimiento = CURRENT_DATE + INTERVAL '8 days'
);

-- =================================================================
-- CREAR NOTIFICACIONES DE PRUEBA
-- =================================================================

-- Limpiar notificaciones antiguas de prueba
DELETE FROM notificaciones WHERE titulo LIKE '%[DEMO]%';

-- Crear notificaciones de prueba para alertas
INSERT INTO notificaciones (tipo, titulo, mensaje, id_insumo, semaforo, dias_restantes, cantidad_afectada, leida, activa) VALUES
('VENCIDO', '[DEMO] Producto vencido', 'Leche Fresca venció hace 1 día', (SELECT id_insumo FROM insumo WHERE codigo = 'INS-004'), 'ROJO', -1, '5 L', false, true),
('USAR_HOY', '[DEMO] Usar hoy', 'Huevos deben usarse hoy', (SELECT id_insumo FROM insumo WHERE codigo = 'INS-006'), 'ROJO', 0, '50 UNIDAD', false, true),
('VENCIMIENTO_PROXIMO', '[DEMO] Por vencer', 'Mantequilla vence en 3 días', (SELECT id_insumo FROM insumo WHERE codigo = 'INS-005'), 'ROJO', 3, '8 KG', false, true),
('VENCIMIENTO_PROXIMO', '[DEMO] Atención vencimiento', 'Levadura vence en 10 días', (SELECT id_insumo FROM insumo WHERE codigo = 'INS-002'), 'AMARILLO', 10, '3 KG', false, true),
('STOCK_CRITICO', '[DEMO] Stock bajo', 'Esencia de Vainilla por debajo del mínimo', (SELECT id_insumo FROM insumo WHERE codigo = 'INS-010'), NULL, NULL, '0.3 L', false, true),
('STOCK_CRITICO', '[DEMO] Sin stock', 'Azúcar Impalpable sin stock', (SELECT id_insumo FROM insumo WHERE codigo = 'INS-008'), NULL, NULL, '0 KG', false, true)
ON CONFLICT DO NOTHING;

-- =================================================================
-- VENTAS DE PRUEBA (historial)
-- =================================================================

-- Crear algunas ventas de ejemplo para reportes
INSERT INTO ventas (numero_venta, fecha_venta, total, metodo_pago, id_user, observaciones, anulado) 
SELECT 
    'VTA-2025-001',
    CURRENT_TIMESTAMP - INTERVAL '2 days',
    15.50,
    'efectivo',
    (SELECT id_user FROM usuario LIMIT 1),
    'Venta de prueba 1',
    false
WHERE NOT EXISTS (SELECT 1 FROM ventas WHERE numero_venta = 'VTA-2025-001');

INSERT INTO ventas (numero_venta, fecha_venta, total, metodo_pago, id_user, observaciones, anulado) 
SELECT 
    'VTA-2025-002',
    CURRENT_TIMESTAMP - INTERVAL '1 day',
    45.00,
    'tarjeta',
    (SELECT id_user FROM usuario LIMIT 1),
    'Venta de prueba 2',
    false
WHERE NOT EXISTS (SELECT 1 FROM ventas WHERE numero_venta = 'VTA-2025-002');

INSERT INTO ventas (numero_venta, fecha_venta, total, metodo_pago, id_user, observaciones, anulado) 
SELECT 
    'VTA-2025-003',
    CURRENT_TIMESTAMP,
    28.00,
    'efectivo',
    (SELECT id_user FROM usuario LIMIT 1),
    'Venta de hoy',
    false
WHERE NOT EXISTS (SELECT 1 FROM ventas WHERE numero_venta = 'VTA-2025-003');

-- =================================================================
-- ÓRDENES DE COMPRA PENDIENTES (para dashboard)
-- =================================================================

INSERT INTO ordenes_compra (numero_orden, fecha_orden, fecha_entrega_estimada, id_proveedor, id_user, monto_total, estado, observaciones)
SELECT 
    'OC-2025-001',
    CURRENT_DATE - INTERVAL '3 days',
    CURRENT_DATE + INTERVAL '2 days',
    (SELECT id_proveedor FROM proveedores LIMIT 1),
    (SELECT id_user FROM usuario LIMIT 1),
    500.00,
    'PENDIENTE',
    'Orden de compra pendiente de entrega'
WHERE NOT EXISTS (SELECT 1 FROM ordenes_compra WHERE numero_orden = 'OC-2025-001');

INSERT INTO ordenes_compra (numero_orden, fecha_orden, fecha_entrega_estimada, id_proveedor, id_user, monto_total, estado, observaciones)
SELECT 
    'OC-2025-002',
    CURRENT_DATE - INTERVAL '1 day',
    CURRENT_DATE + INTERVAL '5 days',
    (SELECT id_proveedor FROM proveedores ORDER BY id_proveedor DESC LIMIT 1),
    (SELECT id_user FROM usuario LIMIT 1),
    320.00,
    'ENVIADA',
    'Orden enviada al proveedor'
WHERE NOT EXISTS (SELECT 1 FROM ordenes_compra WHERE numero_orden = 'OC-2025-002');

-- =================================================================
-- RESUMEN DE DATOS CREADOS
-- =================================================================
SELECT 'Productos terminados con stock:' as info, COUNT(*) as cantidad FROM productos_terminados WHERE stock_actual > 0
UNION ALL
SELECT 'Alertas/Notificaciones:', COUNT(*) FROM notificaciones WHERE activa = true
UNION ALL
SELECT 'Ventas registradas:', COUNT(*) FROM ventas
UNION ALL
SELECT 'Órdenes de compra pendientes:', COUNT(*) FROM ordenes_compra WHERE estado IN ('PENDIENTE', 'ENVIADA');
"""


def load_sales_demo():
    """Cargar datos de demo para pruebas de ventas."""
    print("=" * 60)
    print("Cargando datos de demo para PUNTO DE VENTA...")
    print("=" * 60)

    try:
        with engine.connect() as conn:
            # Primero ejecutar el script principal de demo
            print("\n1. Cargando datos base...")
            try:
                from load_demo_data import load_demo_data
                load_demo_data()
            except Exception as e:
                print(f"   Nota: {str(e)[:50]}... (continuando)")

            # Ejecutar datos específicos de ventas
            print("\n2. Cargando datos de ventas y alertas...")
            statements = [s.strip() for s in SALES_DEMO_SQL.split(';') if s.strip() and not s.strip().startswith('--')]

            success_count = 0
            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        result = conn.execute(text(statement))
                        if result.returns_rows:
                            rows = result.fetchall()
                            for row in rows:
                                print(f"   {row[0]} {row[1]}")
                        success_count += 1
                    except Exception as e:
                        error_msg = str(e)
                        if 'duplicate' in error_msg.lower() or 'already exists' in error_msg.lower():
                            pass  # Ignorar duplicados silenciosamente
                        else:
                            print(f"   ⚠ Statement {i}: {error_msg[:60]}")

            conn.commit()
            
            print("\n" + "=" * 60)
            print("✅ Datos de demo cargados exitosamente!")
            print("=" * 60)
            print("\nPuedes probar:")
            print("  • Dashboard: http://localhost:5173 (frontend)")
            print("  • Punto de Venta: Menú -> Punto de Venta")
            print("  • Alertas: Menú -> Alertas")
            print("  • API Docs: http://localhost:8000/docs")
            print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    load_sales_demo()
