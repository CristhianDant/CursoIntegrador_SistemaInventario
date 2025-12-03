"""Ejecutar job de alertas manualmente"""
import main
from database import SessionLocal
from jobs.alertas_job import ejecutar_alertas_diarias

db = SessionLocal()

print("Ejecutando job de alertas...")
resultado = ejecutar_alertas_diarias(db, 1)

print("Resultado del job:")
print(f"  Alertas vencimiento: {resultado.get('alertas_vencimiento', 0)}")
print(f"  Alertas stock: {resultado.get('alertas_stock', 0)}")

# Verificar notificaciones
from modules.alertas.repository import AlertasRepository
repo = AlertasRepository(db)
notifs = repo.obtener_notificaciones_activas()
print(f"\nNotificaciones en BD ahora: {len(notifs)}")
for n in notifs:
    print(f"  - [{n.tipo}] {n.titulo}")

db.close()
