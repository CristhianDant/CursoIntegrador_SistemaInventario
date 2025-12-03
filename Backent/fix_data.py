"""Script para cargar datos de prueba correctamente."""
from database import engine
from sqlalchemy import text

def load_test_data():
    with engine.connect() as conn:
        # 1. Resetear secuencia de usuarios
        print("Reseteando secuencia de usuarios...")
        conn.execute(text("SELECT setval('usuario_id_user_seq', (SELECT MAX(id_user) FROM usuario))"))
        
        # 2. Insertar usuarios adicionales
        print("Insertando usuarios...")
        usuarios = [
            ('Juan', 'Perez Garcia', 'juan@panaderia.com', 'hashedpassword123'),
            ('Maria', 'Lopez Sanchez', 'maria@panaderia.com', 'hashedpassword123'),
            ('Carlos', 'Ramirez', 'carlos@panaderia.com', 'hashedpassword123'),
        ]
        for nombre, apellido, email, pwd in usuarios:
            try:
                conn.execute(text(
                    "INSERT INTO usuario (nombre, apellidos, email, password) VALUES (:n, :a, :e, :p)"
                ), {'n': nombre, 'a': apellido, 'e': email, 'p': pwd})
                print(f"  ✓ Usuario {nombre} insertado")
            except Exception as ex:
                print(f"  - Usuario {nombre}: ya existe o error")
        
        # 3. Verificar que proveedores existan
        print("\nVerificando proveedores...")
        r = conn.execute(text("SELECT COUNT(*) FROM proveedores"))
        count = r.fetchone()[0]
        if count == 0:
            print("  Insertando proveedores...")
            conn.execute(text("""
                INSERT INTO proveedores (nombre, ruc_dni, numero_contacto, email_contacto, direccion_fiscal) VALUES
                ('Distribuidora Harinas del Sur', '20123456789', '987654321', 'ventas@harinassur.com', 'Av. Industrial 123, Lima'),
                ('Lacteos Gloria', '20987654321', '912345678', 'pedidos@gloria.com', 'Av. Republica de Panama 456, Lima'),
                ('Huevos Don Pepe', '10456789012', '956789012', 'ventas@huevosdonpepe.com', 'Jr. Comercio 789, Lima')
            """))
        print(f"  ✓ Proveedores: {count if count > 0 else 3}")
        
        # 4. Verificar insumos
        print("\nVerificando insumos...")
        r = conn.execute(text("SELECT COUNT(*) FROM insumo"))
        count = r.fetchone()[0]
        if count == 0:
            print("  Insertando insumos...")
            conn.execute(text("""
                INSERT INTO insumo (codigo, nombre, descripcion, unidad_medida, stock_minimo, perecible, categoria) VALUES
                ('INS-001', 'Harina de Trigo', 'Harina de trigo todo uso', 'KG', 50.0, false, 'Harinas'),
                ('INS-002', 'Levadura Seca', 'Levadura instantanea', 'KG', 5.0, true, 'Levaduras'),
                ('INS-003', 'Sal de Mesa', 'Sal refinada', 'KG', 10.0, false, 'Condimentos'),
                ('INS-004', 'Leche Fresca', 'Leche entera pasteurizada', 'L', 20.0, true, 'Lacteos'),
                ('INS-005', 'Mantequilla', 'Mantequilla sin sal', 'KG', 10.0, true, 'Lacteos'),
                ('INS-006', 'Huevos', 'Huevos frescos', 'UNIDAD', 100.0, true, 'Huevos'),
                ('INS-007', 'Azucar Blanca', 'Azucar refinada', 'KG', 30.0, false, 'Azucares')
                ON CONFLICT (codigo) DO NOTHING
            """))
        print(f"  ✓ Insumos: {count if count > 0 else 7}")
        
        # 5. Verificar productos terminados
        print("\nVerificando productos terminados...")
        r = conn.execute(text("SELECT COUNT(*) FROM productos_terminados"))
        count = r.fetchone()[0]
        if count == 0:
            print("  Insertando productos terminados...")
            conn.execute(text("""
                INSERT INTO productos_terminados (codigo_producto, nombre, descripcion, unidad_medida, stock_actual, stock_minimo, vida_util_dias, precio_venta) VALUES
                ('PROD-001', 'Pan Frances', 'Pan frances crujiente', 'UNIDAD', 100, 50, 1, 0.30),
                ('PROD-002', 'Bizcocho de Vainilla', 'Bizcocho esponjoso', 'UNIDAD', 25, 10, 3, 25.00),
                ('PROD-003', 'Empanada de Pollo', 'Empanada rellena', 'UNIDAD', 50, 20, 2, 3.50),
                ('PROD-004', 'Croissant', 'Croissant de mantequilla', 'UNIDAD', 30, 15, 2, 4.00),
                ('PROD-005', 'Pan de Molde', 'Pan de molde integral', 'UNIDAD', 40, 20, 5, 8.00)
                ON CONFLICT (codigo_producto) DO NOTHING
            """))
        print(f"  ✓ Productos terminados: {count if count > 0 else 5}")
        
        # 6. Crear ingresos de insumos (lotes)
        print("\nCreando ingresos de insumos...")
        # Obtener IDs necesarios
        r = conn.execute(text("SELECT id_user FROM usuario LIMIT 1"))
        user_id = r.fetchone()[0]
        
        r = conn.execute(text("SELECT id_proveedor FROM proveedores LIMIT 1"))
        prov_row = r.fetchone()
        if prov_row:
            prov_id = prov_row[0]
            
            try:
                conn.execute(text("""
                    INSERT INTO ingresos_insumos (numero_ingreso, numero_documento, tipo_documento, fecha_ingreso, 
                        fecha_documento, id_user, id_proveedor, observaciones, estado, monto_total)
                    VALUES ('ING-2025-001', 'F001-00123', 'FACTURA', NOW(), CURRENT_DATE, :user_id, :prov_id, 
                        'Compra inicial de insumos', 'COMPLETADO', 500.00)
                    ON CONFLICT (numero_ingreso) DO NOTHING
                """), {'user_id': user_id, 'prov_id': prov_id})
                print("  ✓ Ingreso ING-2025-001 creado")
            except Exception as ex:
                print(f"  - Ingreso ya existe: {str(ex)[:50]}")
        
        conn.commit()
        
        # Resumen final
        print("\n" + "="*50)
        print("RESUMEN DE DATOS EN LA BASE DE DATOS:")
        print("="*50)
        
        tables = [
            ('usuario', 'id_user, nombre, email'),
            ('proveedores', 'id_proveedor, nombre, ruc_dni'),
            ('insumo', 'id_insumo, codigo, nombre'),
            ('productos_terminados', 'id_producto, codigo_producto, nombre, stock_actual, precio_venta'),
        ]
        
        for table, cols in tables:
            print(f"\n--- {table.upper()} ---")
            r = conn.execute(text(f"SELECT {cols} FROM {table}"))
            for row in r:
                print(f"  {row}")

if __name__ == "__main__":
    load_test_data()
