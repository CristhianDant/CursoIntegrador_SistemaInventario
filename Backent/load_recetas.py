"""Script para crear recetas de panadería."""
from database import engine
from sqlalchemy import text

def load_recetas():
    with engine.connect() as conn:
        # 1. Verificar estructura de tablas
        print("Verificando tablas...")
        r = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name LIKE '%receta%'
        """))
        tables = [row[0] for row in r]
        print(f"Tablas de recetas: {tables}")
        
        if not tables:
            print("ERROR: No existen tablas de recetas")
            return
        
        # 2. Ver estructura de recetas
        print("\nEstructura de 'recetas':")
        r = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'recetas' ORDER BY ordinal_position
        """))
        cols_recetas = []
        for row in r:
            print(f"  {row[0]}: {row[1]}")
            cols_recetas.append(row[0])
        
        print("\nEstructura de 'recetas_detalle':")
        r = conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'recetas_detalle' ORDER BY ordinal_position
        """))
        for row in r:
            print(f"  {row[0]}: {row[1]}")
        
        # 3. Obtener productos terminados
        print("\nProductos terminados disponibles:")
        r = conn.execute(text("SELECT id_producto, codigo_producto, nombre FROM productos_terminados"))
        productos = {row[1]: row[0] for row in r}  # codigo -> id
        for codigo, id_prod in productos.items():
            print(f"  {codigo} (ID: {id_prod})")
        
        # 4. Obtener insumos
        print("\nInsumos disponibles:")
        r = conn.execute(text("SELECT id_insumo, codigo, nombre FROM insumo"))
        insumos = {row[1]: (row[0], row[2]) for row in r}  # codigo -> (id, nombre)
        for codigo, (id_ins, nombre) in insumos.items():
            print(f"  {codigo}: {nombre} (ID: {id_ins})")
        
        # 5. Crear recetas
        print("\n" + "="*50)
        print("CREANDO RECETAS...")
        print("="*50)
        
        recetas_data = [
            {
                'producto': 'PROD-001',  # Pan Frances
                'codigo_receta': 'REC-001',
                'nombre': 'Pan Frances Clasico',
                'descripcion': 'Receta tradicional de pan frances crujiente. Rinde 20 unidades.',
                'rendimiento': 20.0,
                'costo_estimado': 5.00,
                'ingredientes': [
                    ('INS-001', 1.0, 3.50, 'Harina base'),      # Harina
                    ('INS-002', 0.02, 25.00, 'Levadura seca'),   # Levadura
                    ('INS-003', 0.02, 1.50, 'Sal fina'),         # Sal
                ]
            },
            {
                'producto': 'PROD-002',  # Bizcocho de Vainilla
                'codigo_receta': 'REC-002',
                'nombre': 'Bizcocho de Vainilla',
                'descripcion': 'Bizcocho esponjoso con esencia de vainilla. Rinde 1 unidad grande.',
                'rendimiento': 1.0,
                'costo_estimado': 15.00,
                'ingredientes': [
                    ('INS-001', 0.30, 3.50, 'Harina tamizada'),   # Harina
                    ('INS-007', 0.25, 4.00, 'Azucar blanca'),     # Azucar
                    ('INS-006', 4.0, 0.50, '4 huevos grandes'),   # Huevos
                    ('INS-005', 0.15, 18.00, 'Mantequilla derretida'), # Mantequilla
                    ('INS-004', 0.20, 5.00, 'Leche temperatura ambiente'), # Leche
                ]
            },
            {
                'producto': 'PROD-003',  # Empanada de Pollo
                'codigo_receta': 'REC-003',
                'nombre': 'Empanada de Pollo',
                'descripcion': 'Masa para empanadas rellenas de pollo. Rinde 10 unidades.',
                'rendimiento': 10.0,
                'costo_estimado': 12.00,
                'ingredientes': [
                    ('INS-001', 0.50, 3.50, 'Harina para masa'),  # Harina
                    ('INS-005', 0.10, 18.00, 'Mantequilla fria'), # Mantequilla
                    ('INS-003', 0.01, 1.50, 'Sal'),               # Sal
                    ('INS-006', 1.0, 0.50, 'Huevo para barnizar'), # Huevo
                ]
            },
            {
                'producto': 'PROD-004',  # Croissant
                'codigo_receta': 'REC-004',
                'nombre': 'Croissant de Mantequilla',
                'descripcion': 'Croissant hojaldrado con capas de mantequilla. Rinde 8 unidades.',
                'rendimiento': 8.0,
                'costo_estimado': 18.00,
                'ingredientes': [
                    ('INS-001', 0.50, 3.50, 'Harina de fuerza'),  # Harina
                    ('INS-005', 0.25, 18.00, 'Mantequilla para laminado'), # Mantequilla
                    ('INS-002', 0.01, 25.00, 'Levadura'),         # Levadura
                    ('INS-004', 0.15, 5.00, 'Leche tibia'),       # Leche
                    ('INS-007', 0.03, 4.00, 'Azucar'),            # Azucar
                    ('INS-003', 0.01, 1.50, 'Sal'),               # Sal
                    ('INS-006', 1.0, 0.50, 'Huevo para barnizar'), # Huevo
                ]
            },
        ]
        
        for receta in recetas_data:
            try:
                id_producto = productos.get(receta['producto'])
                if not id_producto:
                    print(f"  ⚠ Producto {receta['producto']} no encontrado")
                    continue
                
                # Insertar receta
                conn.execute(text("""
                    INSERT INTO recetas (id_producto, codigo_receta, nombre_receta, descripcion, 
                        rendimiento_producto_terminado, costo_estimado, estado)
                    VALUES (:id_prod, :codigo, :nombre, :desc, :rend, :costo, 'ACTIVA')
                    ON CONFLICT (codigo_receta) DO NOTHING
                """), {
                    'id_prod': id_producto,
                    'codigo': receta['codigo_receta'],
                    'nombre': receta['nombre'],
                    'desc': receta['descripcion'],
                    'rend': receta['rendimiento'],
                    'costo': receta['costo_estimado']
                })
                print(f"  ✓ Receta '{receta['nombre']}' creada")
                
                # Obtener ID de la receta
                r = conn.execute(text(
                    "SELECT id_receta FROM recetas WHERE codigo_receta = :codigo"
                ), {'codigo': receta['codigo_receta']})
                row = r.fetchone()
                if not row:
                    continue
                id_receta = row[0]
                
                # Insertar ingredientes
                for ing_codigo, cantidad, precio, obs in receta['ingredientes']:
                    if ing_codigo not in insumos:
                        print(f"    ⚠ Insumo {ing_codigo} no encontrado")
                        continue
                    
                    id_insumo = insumos[ing_codigo][0]
                    try:
                        conn.execute(text("""
                            INSERT INTO recetas_detalle (id_receta, id_insumo, cantidad, costo_unitario, 
                                es_opcional, observaciones)
                            VALUES (:id_rec, :id_ins, :cant, :precio, false, :obs)
                            ON CONFLICT DO NOTHING
                        """), {
                            'id_rec': id_receta,
                            'id_ins': id_insumo,
                            'cant': cantidad,
                            'precio': precio,
                            'obs': obs
                        })
                        print(f"    + {insumos[ing_codigo][1]}: {cantidad}")
                    except Exception as e:
                        print(f"    - Error ingrediente: {str(e)[:50]}")
                
            except Exception as e:
                print(f"  ✗ Error en receta {receta['codigo_receta']}: {e}")
        
        conn.commit()
        
        # 6. Verificar recetas creadas
        print("\n" + "="*50)
        print("RECETAS CREADAS:")
        print("="*50)
        r = conn.execute(text("""
            SELECT r.codigo_receta, r.nombre_receta, p.nombre as producto, r.rendimiento_producto_terminado, r.estado
            FROM recetas r
            JOIN productos_terminados p ON r.id_producto = p.id_producto
            ORDER BY r.codigo_receta
        """))
        for row in r:
            print(f"  {row[0]}: {row[1]} -> {row[2]} (Rinde: {row[3]}, Estado: {row[4]})")
        
        print("\nDETALLE DE INGREDIENTES:")
        r = conn.execute(text("""
            SELECT r.codigo_receta, i.nombre, rd.cantidad, i.unidad_medida, rd.observaciones
            FROM recetas_detalle rd
            JOIN recetas r ON rd.id_receta = r.id_receta
            JOIN insumo i ON rd.id_insumo = i.id_insumo
            ORDER BY r.codigo_receta, i.nombre
        """))
        current_receta = None
        for row in r:
            if row[0] != current_receta:
                current_receta = row[0]
                print(f"\n  [{current_receta}]")
            print(f"    - {row[1]}: {row[2]} {row[3]} ({row[4]})")

if __name__ == "__main__":
    load_recetas()
