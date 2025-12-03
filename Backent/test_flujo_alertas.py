"""
Script para probar el flujo completo:
1. Crear orden de compra
2. Crear ingreso con fecha de vencimiento próxima (mañana)
3. Completar el ingreso
4. Verificar alertas
"""
import main  # Cargar todos los modelos
from database import SessionLocal
from sqlalchemy import text
from datetime import datetime, timedelta
from decimal import Decimal

db = SessionLocal()

print("=" * 60)
print("PRUEBA DE FLUJO COMPLETO: ORDEN -> INGRESO -> ALERTAS")
print("=" * 60)

# ============================================================
# 1. CREAR ORDEN DE COMPRA
# ============================================================
print("\n1. CREANDO ORDEN DE COMPRA...")

# Obtener un proveedor existente
proveedor = db.execute(text("SELECT id_proveedor, nombre FROM proveedores WHERE anulado = false LIMIT 1")).fetchone()
if not proveedor:
    print("   ERROR: No hay proveedores. Creando uno...")
    db.execute(text("""
        INSERT INTO proveedores (nombre, ruc, direccion, telefono, email, estado)
        VALUES ('Proveedor Test', '12345678901', 'Av. Test 123', '999888777', 'test@test.com', true)
    """))
    db.commit()
    proveedor = db.execute(text("SELECT id_proveedor, nombre FROM proveedores WHERE anulado = false LIMIT 1")).fetchone()

print(f"   Proveedor: {proveedor.nombre} (ID: {proveedor.id_proveedor})")

# Obtener un usuario existente
usuario = db.execute(text("SELECT id_user FROM usuario LIMIT 1")).fetchone()
if not usuario:
    print("   ERROR: No hay usuarios")
    db.close()
    exit(1)

# Obtener un insumo perecible (Leche)
insumo = db.execute(text("SELECT id_insumo, nombre, codigo FROM insumo WHERE perecible = true AND anulado = false LIMIT 1")).fetchone()
if not insumo:
    print("   ERROR: No hay insumos perecibles. Creando uno...")
    db.execute(text("""
        INSERT INTO insumo (codigo, nombre, unidad_medida, stock_minimo, perecible, categoria)
        VALUES ('INS-TEST', 'Yogurt Test', 'UNIDAD', 5, true, 'Lacteos')
    """))
    db.commit()
    insumo = db.execute(text("SELECT id_insumo, nombre, codigo FROM insumo WHERE perecible = true AND anulado = false LIMIT 1")).fetchone()

print(f"   Insumo perecible: {insumo.nombre} (ID: {insumo.id_insumo})")

# Generar número de orden único
numero_orden = f"OC-TEST-{datetime.now().strftime('%H%M%S')}"

# Crear la orden de compra
db.execute(text("""
    INSERT INTO orden_de_compra 
    (numero_orden, id_proveedor, fecha_orden, fecha_entrega_esperada, moneda, tipo_cambio, sub_total, descuento, igv, total, estado, id_user_creador)
    VALUES 
    (:numero_orden, :id_proveedor, NOW(), NOW() + INTERVAL '2 days', 'PEN', 1, 50.00, 0, 9.00, 59.00, 'APROBADO', :id_user)
"""), {
    "numero_orden": numero_orden,
    "id_proveedor": proveedor.id_proveedor,
    "id_user": usuario.id_user
})
db.commit()

# Obtener ID de la orden creada
orden = db.execute(text("SELECT id_orden FROM orden_de_compra WHERE numero_orden = :num"), {"num": numero_orden}).fetchone()
print(f"   ✅ Orden de compra creada: {numero_orden} (ID: {orden.id_orden})")

# Agregar detalle a la orden
db.execute(text("""
    INSERT INTO orden_de_compra_detalle 
    (id_orden, id_insumo, cantidad, precio_unitario, descuento_unitario, sub_total)
    VALUES 
    (:id_orden, :id_insumo, 10, 5.00, 0, 50.00)
"""), {
    "id_orden": orden.id_orden,
    "id_insumo": insumo.id_insumo
})
db.commit()
print(f"   ✅ Detalle agregado: {insumo.nombre} x 10 unidades")

# ============================================================
# 2. CREAR INGRESO CON FECHA DE VENCIMIENTO PRÓXIMA
# ============================================================
print("\n2. CREANDO INGRESO DE INSUMOS (VENCE MAÑANA)...")

numero_ingreso = f"ING-TEST-{datetime.now().strftime('%H%M%S')}"
fecha_vencimiento = datetime.now() + timedelta(days=1)  # Vence mañana!

# Crear el ingreso en estado PENDIENTE primero
db.execute(text("""
    INSERT INTO ingresos_insumos 
    (numero_ingreso, id_orden_compra, numero_documento, tipo_documento, fecha_registro, fecha_ingreso, fecha_documento, id_user, id_proveedor, estado, monto_total, anulado)
    VALUES 
    (:numero_ingreso, :id_orden, 'FAC-TEST-001', 'FACTURA', NOW(), NOW(), NOW(), :id_user, :id_proveedor, 'PENDIENTE', 50.00, false)
"""), {
    "numero_ingreso": numero_ingreso,
    "id_orden": orden.id_orden,
    "id_user": usuario.id_user,
    "id_proveedor": proveedor.id_proveedor
})
db.commit()

# Obtener ID del ingreso
ingreso = db.execute(text("SELECT id_ingreso FROM ingresos_insumos WHERE numero_ingreso = :num"), {"num": numero_ingreso}).fetchone()
print(f"   ✅ Ingreso creado: {numero_ingreso} (ID: {ingreso.id_ingreso}) - Estado: PENDIENTE")

# Agregar detalle con fecha de vencimiento próxima
db.execute(text("""
    INSERT INTO ingresos_insumos_detalle 
    (id_ingreso, id_insumo, cantidad_ordenada, cantidad_ingresada, precio_unitario, subtotal, fecha_vencimiento, cantidad_restante)
    VALUES 
    (:id_ingreso, :id_insumo, 10, 10, 5.00, 50.00, :fecha_vencimiento, 0)
"""), {
    "id_ingreso": ingreso.id_ingreso,
    "id_insumo": insumo.id_insumo,
    "fecha_vencimiento": fecha_vencimiento
})
db.commit()
print(f"   ✅ Detalle agregado con vencimiento: {fecha_vencimiento.strftime('%Y-%m-%d')} (¡MAÑANA!)")

# ============================================================
# 3. COMPLETAR EL INGRESO (esto actualiza el stock)
# ============================================================
print("\n3. COMPLETANDO EL INGRESO (actualiza stock)...")

# Actualizar estado a COMPLETADO y cantidad_restante
db.execute(text("""
    UPDATE ingresos_insumos SET estado = 'COMPLETADO' WHERE id_ingreso = :id_ingreso
"""), {"id_ingreso": ingreso.id_ingreso})

db.execute(text("""
    UPDATE ingresos_insumos_detalle SET cantidad_restante = cantidad_ingresada WHERE id_ingreso = :id_ingreso
"""), {"id_ingreso": ingreso.id_ingreso})

# Actualizar orden de compra a COMPLETADO
db.execute(text("""
    UPDATE orden_de_compra SET estado = 'COMPLETADO' WHERE id_orden = :id_orden
"""), {"id_orden": orden.id_orden})

db.commit()
print(f"   ✅ Ingreso COMPLETADO - cantidad_restante actualizada")
print(f"   ✅ Orden de compra COMPLETADA")

# ============================================================
# 4. VERIFICAR ALERTAS
# ============================================================
print("\n4. VERIFICANDO ALERTAS...")

from modules.alertas.repository import AlertasRepository
repo = AlertasRepository(db)

# Verificar lotes por vencer
lotes = repo.obtener_lotes_por_vencer(dias_limite=7)
print(f"\n   LOTES POR VENCER (próximos 7 días): {len(lotes)}")
for l in lotes:
    print(f"      - {l['nombre_insumo']}: vence en {l['dias_restantes']} día(s), cantidad: {l['cantidad_restante']}")

# Verificar semáforo
semaforo = repo.obtener_resumen_semaforo(dias_verde=15, dias_amarillo=7, dias_rojo=3)
print(f"\n   SEMÁFORO:")
print(f"      🟢 Verde: {semaforo.get('VERDE', 0)}")
print(f"      🟡 Amarillo: {semaforo.get('AMARILLO', 0)}")
print(f"      🔴 Rojo: {semaforo.get('ROJO', 0)}")
print(f"      ⚫ Vencido: {semaforo.get('VENCIDO', 0)}")

# Verificar lista usar hoy
usar_hoy = repo.obtener_lista_usar_hoy(dias_rojo=3)
print(f"\n   USAR HOY/URGENTE: {len(usar_hoy)}")
for item in usar_hoy:
    print(f"      - {item['nombre_insumo']}: {item['dias_restantes']} día(s), cantidad: {item['cantidad_restante']}")

# Verificar notificaciones en BD
notifs = repo.obtener_notificaciones_activas()
print(f"\n   NOTIFICACIONES EN BD: {len(notifs)}")

print("\n" + "=" * 60)
print("✅ PRUEBA COMPLETADA")
print("=" * 60)
print("\nAhora ve al frontend y revisa la sección de ALERTAS.")
print("Deberías ver el insumo que vence mañana en ROJO.")

db.close()
