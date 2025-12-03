"""Script para verificar el estado del stock y alertas"""
from database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

print("=" * 60)
print("INSUMOS CON STOCK BAJO O CERO")
print("=" * 60)

# El stock_actual se calcula desde ingresos_insumos_detalle (cantidad_restante)
result = db.execute(text("""
    SELECT 
        i.id_insumo, 
        i.codigo,
        i.nombre, 
        i.stock_minimo, 
        i.unidad_medida,
        COALESCE(SUM(iid.cantidad_restante), 0) as stock_actual
    FROM insumo i
    LEFT JOIN ingresos_insumos_detalle iid ON i.id_insumo = iid.id_insumo
    WHERE i.anulado = false
    GROUP BY i.id_insumo, i.codigo, i.nombre, i.stock_minimo, i.unidad_medida
    HAVING COALESCE(SUM(iid.cantidad_restante), 0) <= i.stock_minimo
    ORDER BY stock_actual ASC
    LIMIT 15
"""))

for row in result:
    status = "🔴 AGOTADO" if float(row.stock_actual) == 0 else "🟡 BAJO"
    print(f"{status} | ID:{row.id_insumo} | {row.nombre}")
    print(f"         Stock: {row.stock_actual} / Min: {row.stock_minimo} {row.unidad_medida}")

print("\n" + "=" * 60)
print("ALERTAS ACTIVAS")
print("=" * 60)

alertas = db.execute(text("""
    SELECT id_alerta, tipo_alerta, titulo, estado
    FROM alertas 
    WHERE estado = 'PENDIENTE'
    ORDER BY fecha_creacion DESC
    LIMIT 15
"""))

count = 0
for a in alertas:
    emoji = "⚠️" if "STOCK" in a.tipo_alerta else "📢"
    print(f"{emoji} [{a.tipo_alerta}] {a.titulo}")
    count += 1

if count == 0:
    print("✅ No hay alertas pendientes")

print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)

# Contar totales usando la misma lógica de stock calculado
total_insumos = db.execute(text("SELECT COUNT(*) FROM insumo WHERE anulado = false")).scalar()

stock_data = db.execute(text("""
    SELECT 
        COUNT(CASE WHEN stock = 0 THEN 1 END) as sin_stock,
        COUNT(CASE WHEN stock > 0 AND stock <= stock_minimo THEN 1 END) as stock_bajo
    FROM (
        SELECT 
            i.id_insumo,
            i.stock_minimo,
            COALESCE(SUM(iid.cantidad_restante), 0) as stock
        FROM insumo i
        LEFT JOIN ingresos_insumos_detalle iid ON i.id_insumo = iid.id_insumo
        WHERE i.anulado = false
        GROUP BY i.id_insumo, i.stock_minimo
    ) subq
""")).first()

alertas_pendientes = db.execute(text("SELECT COUNT(*) FROM alertas WHERE estado = 'PENDIENTE'")).scalar()

print(f"Total insumos: {total_insumos}")
print(f"Sin stock (0): {stock_data.sin_stock}")
print(f"Stock bajo: {stock_data.stock_bajo}")
print(f"Alertas pendientes: {alertas_pendientes}")

db.close()
