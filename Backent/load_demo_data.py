"""
Script para cargar datos de demo a la base de datos.
Ejecutar desde el directorio Backent:
    python load_demo_data.py
"""

from sqlalchemy import text
from database import engine

# SQL de demo data
DEMO_SQL = """
-- =================================================================
-- DEMO: Panadería - Datos de prueba para endpoints FEFO y Producción
-- =================================================================

-- Crear usuario admin si no existe
INSERT INTO usuario (nombre, apellidos, email, password)
VALUES ('Admin', 'Panadería', 'admin@panaderia.com', 'hash_password_aqui')
ON CONFLICT (email) DO NOTHING;

-- =================================================================
-- 1. PROVEEDORES
-- =================================================================

INSERT INTO proveedores (nombre, ruc_dni, numero_contacto, email_contacto, direccion_fiscal) VALUES
('Distribuidora Harinas del Sur', '20123456789', '987654321', 'ventas@harinassur.com', 'Av. Industrial 123, Lima'),
('Lácteos Gloria', '20987654321', '912345678', 'pedidos@gloria.com', 'Av. República de Panamá 456, Lima'),
('Huevos Don Pepe', '10456789012', '956789012', 'ventas@huevosdonpepe.com', 'Jr. Comercio 789, Lima')
ON CONFLICT DO NOTHING;

-- =================================================================
-- 2. INSUMOS
-- =================================================================

INSERT INTO insumo (codigo, nombre, descripcion, unidad_medida, stock_minimo, perecible, categoria) VALUES
('INS-001', 'Harina de Trigo', 'Harina de trigo todo uso para panadería', 'KG', 50.0000, false, 'Harinas'),
('INS-002', 'Levadura Seca', 'Levadura instantánea para pan', 'KG', 5.0000, true, 'Levaduras'),
('INS-003', 'Sal de Mesa', 'Sal refinada para cocina', 'KG', 10.0000, false, 'Condimentos'),
('INS-004', 'Leche Fresca', 'Leche entera pasteurizada', 'L', 20.0000, true, 'Lacteos'),
('INS-005', 'Mantequilla', 'Mantequilla sin sal', 'KG', 10.0000, true, 'Lacteos'),
('INS-006', 'Huevos', 'Huevos frescos de gallina', 'UNIDAD', 100.0000, true, 'Huevos'),
('INS-007', 'Azúcar Blanca', 'Azúcar refinada', 'KG', 30.0000, false, 'Azucares'),
('INS-008', 'Azúcar Impalpable', 'Azúcar en polvo para decoración', 'KG', 5.0000, false, 'Azucares'),
('INS-009', 'Aceite Vegetal', 'Aceite de soya refinado', 'L', 15.0000, false, 'Aceites'),
('INS-010', 'Esencia de Vainilla', 'Extracto puro de vainilla', 'L', 2.0000, false, 'Esencias')
ON CONFLICT (codigo) DO NOTHING;

-- =================================================================
-- 3. PRODUCTOS TERMINADOS
-- =================================================================

INSERT INTO productos_terminados (codigo_producto, nombre, descripcion, unidad_medida, stock_actual, stock_minimo, vida_util_dias, precio_venta) VALUES
('PROD-001', 'Pan Francés', 'Pan francés crujiente tradicional', 'UNIDAD', 0, 50, 1, 0.30),
('PROD-002', 'Bizcocho de Vainilla', 'Bizcocho esponjoso sabor vainilla', 'UNIDAD', 0, 10, 3, 25.00)
ON CONFLICT (codigo_producto) DO NOTHING;

-- =================================================================
-- 4. RECETAS
-- =================================================================

INSERT INTO recetas (id_producto, codigo_receta, nombre_receta, descripcion, rendimiento_producto_terminado, costo_estimado, estado)
SELECT id_producto, 'REC-001', 'Pan Francés Clásico', 'Receta tradicional de pan francés crujiente', 20.0000, 5.00, 'ACTIVA'
FROM productos_terminados WHERE codigo_producto = 'PROD-001'
ON CONFLICT (codigo_receta) DO NOTHING;

INSERT INTO recetas (id_producto, codigo_receta, nombre_receta, descripcion, rendimiento_producto_terminado, costo_estimado, estado)
SELECT id_producto, 'REC-002', 'Bizcocho de Vainilla', 'Bizcocho esponjoso con esencia de vainilla', 1.0000, 15.00, 'ACTIVA'
FROM productos_terminados WHERE codigo_producto = 'PROD-002'
ON CONFLICT (codigo_receta) DO NOTHING;

-- =================================================================
-- 5. DETALLE DE RECETAS
-- =================================================================

-- Detalle RECETA 1: Pan Francés
INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 1.0000, 3.50, false, 'Harina todo uso'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-001' AND i.codigo = 'INS-001'
ON CONFLICT DO NOTHING;

INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 0.0200, 25.00, false, 'Levadura instantánea'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-001' AND i.codigo = 'INS-002'
ON CONFLICT DO NOTHING;

INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 0.0200, 1.50, false, 'Sal fina'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-001' AND i.codigo = 'INS-003'
ON CONFLICT DO NOTHING;

INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 0.0500, 8.00, true, 'Opcional para la masa'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-001' AND i.codigo = 'INS-009'
ON CONFLICT DO NOTHING;

-- Detalle RECETA 2: Bizcocho de Vainilla
INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 0.3000, 3.50, false, 'Harina tamizada'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-002' AND i.codigo = 'INS-001'
ON CONFLICT DO NOTHING;

INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 0.2500, 4.00, false, 'Azúcar blanca'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-002' AND i.codigo = 'INS-007'
ON CONFLICT DO NOTHING;

INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 4.0000, 0.50, false, '4 huevos grandes'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-002' AND i.codigo = 'INS-006'
ON CONFLICT DO NOTHING;

INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 0.1500, 18.00, false, 'Mantequilla derretida'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-002' AND i.codigo = 'INS-005'
ON CONFLICT DO NOTHING;

INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 0.2000, 5.00, false, 'Leche a temperatura ambiente'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-002' AND i.codigo = 'INS-004'
ON CONFLICT DO NOTHING;

INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 0.0100, 80.00, false, 'Esencia pura'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-002' AND i.codigo = 'INS-010'
ON CONFLICT DO NOTHING;

INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, es_opcional, observaciones)
SELECT r.id_receta, i.id_insumo, 0.0100, 25.00, false, 'Polvo de hornear'
FROM recetas r, insumo i WHERE r.codigo_receta = 'REC-002' AND i.codigo = 'INS-002'
ON CONFLICT DO NOTHING;

-- =================================================================
-- 6. INGRESOS DE INSUMOS (Lotes para probar FEFO)
-- =================================================================

-- INGRESO 1: Compra de Harinas
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total)
SELECT 'ING-2025-001', 'F001-00123', 'FACTURA', '2025-11-20 10:00:00', '2025-11-20',
 u.id_user, p.id_proveedor, 'Compra inicial de harinas', 'COMPLETADO', 350.00
FROM usuario u, proveedores p
WHERE u.email = 'admin@panaderia.com' AND p.ruc_dni = '20123456789'
ON CONFLICT (numero_ingreso) DO NOTHING;

-- Detalle INGRESO 1
INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 50.0000, 3.50, 175.00, '2026-05-20', 50.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-001' AND i.codigo = 'INS-001'
ON CONFLICT DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 5.0000, 25.00, 125.00, '2026-02-20', 5.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-001' AND i.codigo = 'INS-002'
ON CONFLICT DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 20.0000, 1.50, 30.00, '2027-11-20', 20.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-001' AND i.codigo = 'INS-003'
ON CONFLICT DO NOTHING;

-- INGRESO 2: Compra de Lácteos
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total)
SELECT 'ING-2025-002', 'F001-00456', 'FACTURA', '2025-11-22 09:00:00', '2025-11-22',
 u.id_user, p.id_proveedor, 'Compra de lácteos frescos', 'COMPLETADO', 280.00
FROM usuario u, proveedores p
WHERE u.email = 'admin@panaderia.com' AND p.ruc_dni = '20987654321'
ON CONFLICT (numero_ingreso) DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 20.0000, 5.00, 100.00, '2025-12-03', 20.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-002' AND i.codigo = 'INS-004'
ON CONFLICT DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 10.0000, 18.00, 180.00, '2025-12-26', 10.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-002' AND i.codigo = 'INS-005'
ON CONFLICT DO NOTHING;

-- INGRESO 3: Compra de Huevos (Lote antiguo)
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total)
SELECT 'ING-2025-003', 'F001-00789', 'FACTURA', '2025-11-15 08:00:00', '2025-11-15',
 u.id_user, p.id_proveedor, 'Compra de huevos - Lote antiguo', 'COMPLETADO', 75.00
FROM usuario u, proveedores p
WHERE u.email = 'admin@panaderia.com' AND p.ruc_dni = '10456789012'
ON CONFLICT (numero_ingreso) DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 150.0000, 0.50, 75.00, '2025-12-01', 150.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-003' AND i.codigo = 'INS-006'
ON CONFLICT DO NOTHING;

-- INGRESO 4: Segunda compra de Huevos (Lote más nuevo)
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total)
SELECT 'ING-2025-004', 'F001-00890', 'FACTURA', '2025-11-25 08:00:00', '2025-11-25',
 u.id_user, p.id_proveedor, 'Compra de huevos - Lote nuevo', 'COMPLETADO', 100.00
FROM usuario u, proveedores p
WHERE u.email = 'admin@panaderia.com' AND p.ruc_dni = '10456789012'
ON CONFLICT (numero_ingreso) DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 200.0000, 0.50, 100.00, '2025-12-11', 200.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-004' AND i.codigo = 'INS-006'
ON CONFLICT DO NOTHING;

-- INGRESO 5: Compra de Azúcares y Esencias
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total)
SELECT 'ING-2025-005', 'F001-00999', 'FACTURA', '2025-11-18 11:00:00', '2025-11-18',
 u.id_user, p.id_proveedor, 'Compra de azúcares y esencias', 'COMPLETADO', 380.00
FROM usuario u, proveedores p
WHERE u.email = 'admin@panaderia.com' AND p.ruc_dni = '20123456789'
ON CONFLICT (numero_ingreso) DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 50.0000, 4.00, 200.00, '2027-11-18', 50.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-005' AND i.codigo = 'INS-007'
ON CONFLICT DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 10.0000, 6.00, 60.00, '2027-11-18', 10.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-005' AND i.codigo = 'INS-008'
ON CONFLICT DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 10.0000, 8.00, 80.00, '2027-11-18', 10.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-005' AND i.codigo = 'INS-009'
ON CONFLICT DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 0.5000, 80.00, 40.00, '2027-11-18', 0.5000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-005' AND i.codigo = 'INS-010'
ON CONFLICT DO NOTHING;

-- INGRESO 6: Compra adicional de Harina (vencimiento próximo)
INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total)
SELECT 'ING-2025-006', 'F001-01000', 'FACTURA', '2025-11-27 12:00:00', '2025-11-27',
 u.id_user, p.id_proveedor, 'Compra adicional de harina - vence pronto', 'COMPLETADO', 140.00
FROM usuario u, proveedores p
WHERE u.email = 'admin@panaderia.com' AND p.ruc_dni = '20123456789'
ON CONFLICT (numero_ingreso) DO NOTHING;

INSERT INTO ingresos_insumos_detalle (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
SELECT ii.id_ingreso, i.id_insumo, 40.0000, 3.50, 140.00, '2025-12-27', 40.0000
FROM ingresos_insumos ii, insumo i
WHERE ii.numero_ingreso = 'ING-2025-006' AND i.codigo = 'INS-001'
ON CONFLICT DO NOTHING;
"""


def load_demo_data():
    """Cargar datos de demo a la base de datos."""
    print("=" * 60)
    print("Cargando datos de demo a la base de datos...")
    print("=" * 60)

    try:
        with engine.connect() as conn:
            # Ejecutar cada statement por separado
            statements = [s.strip() for s in DEMO_SQL.split(';') if s.strip() and not s.strip().startswith('--')]

            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        conn.execute(text(statement))
                        print(f"✓ Statement {i} ejecutado correctamente")
                    except Exception as e:
                        print(f"⚠ Statement {i} - Error (posible duplicado): {str(e)[:80]}")

            conn.commit()
            print("\n" + "=" * 60)
            print("✓ Datos de demo cargados exitosamente!")
            print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error al cargar datos: {e}")
        raise


if __name__ == "__main__":
    load_demo_data()