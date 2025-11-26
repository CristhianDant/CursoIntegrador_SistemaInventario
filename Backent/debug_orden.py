from database import SessionLocal
from modules.orden_de_compra.model import OrdenDeCompra

db = SessionLocal()
orden8 = db.query(OrdenDeCompra).filter(OrdenDeCompra.id_orden == 8).first()
if orden8:
    print(f'Orden 8: anulado={orden8.anulado}, estado={orden8.estado}')
else:
    print('Orden 8 NO EXISTE en la BD')

# Ver todas las órdenes
todas = db.query(OrdenDeCompra).all()
print(f'Todas las órdenes: {[(o.id_orden, o.anulado) for o in todas]}')

# Ver órdenes no anuladas
no_anuladas = db.query(OrdenDeCompra).filter(OrdenDeCompra.anulado == False).all()
print(f'Órdenes no anuladas (IDs): {[o.id_orden for o in no_anuladas]}')
