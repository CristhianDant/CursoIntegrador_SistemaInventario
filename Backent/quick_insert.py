"""Insertar ingresos de insumos de prueba directamente"""
from database import SessionLocal
from sqlalchemy import text
from datetime import datetime, timedelta

db = SessionLocal()
fecha_venc = datetime.now() + timedelta(days=90)

print("=" * 60)
print("INSERTANDO STOCK DE INSUMOS FALTANTES")
print("=" * 60)

# Usar id_ingreso = 1 que existe (ING-2025-001)
id_ingreso = 1

# Insumos que necesitan stock:
# ID:1 Harina de Trigo (min 50 KG)
# ID:5 Mantequilla (min 10 KG) 
# ID:6 Huevos (min 100 UNIDAD)
# ID:7 Azucar Blanca (min 30 KG)
# ID:8 Azucar Impalpable (min 5 KG)

insumos_a_ingresar = [
    (1, "Harina de Trigo", 100, 3.50),
    (5, "Mantequilla", 30, 18.00),
    (6, "Huevos", 200, 0.50),
    (7, "Azucar Blanca", 80, 4.00),
    (8, "Azucar Impalpable", 20, 6.00),
]

for id_insumo, nombre, cantidad, precio in insumos_a_ingresar:
    subtotal = cantidad * precio
    try:
        db.execute(text("""
            INSERT INTO ingresos_insumos_detalle 
            (id_ingreso, id_insumo, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante, cantidad_ordenada)
            VALUES (:id_ing, :id_ins, :cant, :precio, :subtotal, :fecha_venc, :cant_rest, :cant_ord)
        """), {
            'id_ing': id_ingreso,
            'id_ins': id_insumo,
            'cant': cantidad,
            'precio': precio,
            'subtotal': subtotal,
            'fecha_venc': fecha_venc,
            'cant_rest': cantidad,
            'cant_ord': cantidad
        })
        print(f"✅ {nombre}: +{cantidad} unidades (S/{subtotal:.2f})")
    except Exception as e:
        print(f"❌ Error {nombre}: {e}")

db.commit()

# Verificar resultado
print("\n" + "=" * 60)
print("STOCK ACTUALIZADO")
print("=" * 60)

r = db.execute(text("""
    SELECT i.id_insumo, i.nombre, i.stock_minimo, 
           COALESCE(SUM(iid.cantidad_restante), 0) as stock
    FROM insumo i
    LEFT JOIN ingresos_insumos_detalle iid ON i.id_insumo = iid.id_insumo
    WHERE i.anulado = false
    GROUP BY i.id_insumo, i.nombre, i.stock_minimo
    ORDER BY i.nombre
"""))

for row in r:
    stock = float(row.stock)
    minimo = float(row.stock_minimo)
    if stock >= minimo:
        status = "✅"
    elif stock > 0:
        status = "⚠️"
    else:
        status = "🔴"
    print(f"{status} {row.nombre}: {stock} (min: {minimo})")

db.close()
print("\n🎉 ¡Listo! Ya puedes probar la producción.")
