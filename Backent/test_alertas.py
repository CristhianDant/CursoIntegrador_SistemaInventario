"""Script para probar las alertas"""
# Importar main para que cargue todos los modelos correctamente
import main  # Esto registra todos los modelos
from database import SessionLocal
from modules.alertas.repository import AlertasRepository
from modules.alertas.service import AlertasService

db = SessionLocal()

print("=" * 50)
print("DIAGNÓSTICO DE ALERTAS")
print("=" * 50)

# Probar repository
repo = AlertasRepository(db)

print("\n1. LOTES POR VENCER (próximos 15 días):")
lotes = repo.obtener_lotes_por_vencer(dias_limite=15)
print(f"   Total encontrados: {len(lotes)}")
for l in lotes:
    print(f"   - {l['nombre_insumo']}: vence en {l['dias_restantes']} días, cantidad: {l['cantidad_restante']}")

print("\n2. RESUMEN SEMÁFORO:")
semaforo = repo.obtener_resumen_semaforo(dias_verde=15, dias_amarillo=7, dias_rojo=3)
print(f"   Verde: {semaforo.get('VERDE', 0)}")
print(f"   Amarillo: {semaforo.get('AMARILLO', 0)}")
print(f"   Rojo: {semaforo.get('ROJO', 0)}")
print(f"   Vencido: {semaforo.get('VENCIDO', 0)}")

print("\n3. LISTA USAR HOY (próximos 3 días):")
usar_hoy = repo.obtener_lista_usar_hoy(dias_rojo=3)
print(f"   Total: {len(usar_hoy)}")
for item in usar_hoy:
    print(f"   - {item['nombre_insumo']}: {item['dias_restantes']} días, cantidad: {item['cantidad_restante']}")

# Probar service
print("\n4. SERVICIO - SEMÁFORO VENCIMIENTOS:")
service = AlertasService(db)
result = service.obtener_semaforo_vencimientos()
print(f"   Verde: {result.total_verde}")
print(f"   Amarillo: {result.total_amarillo}")
print(f"   Rojo: {result.total_rojo}")
print(f"   Vencido: {result.total_vencidos}")
print(f"   Items rojos: {len(result.items_rojo)}")
for item in result.items_rojo:
    print(f"      - {item.nombre}: {item.dias_restantes} días")

print("\n" + "=" * 50)
db.close()
