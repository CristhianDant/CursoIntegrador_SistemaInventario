from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import date, timedelta
from decimal import Decimal
from modules.orden_de_compra.model import OrdenDeCompra, OrdenDeCompraDetalle
from modules.orden_de_compra.schemas import OrdenDeCompraCreate, OrdenDeCompraUpdate
from modules.orden_de_compra.repository_interface import OrdenDeCompraRepositoryInterface

class OrdenDeCompraRepository(OrdenDeCompraRepositoryInterface):
    def get_all(self, db: Session, activas_solo: bool = True) -> List[OrdenDeCompra]:
        if activas_solo:
            ordenes = db.query(OrdenDeCompra).filter(OrdenDeCompra.anulado == False).all()
        else:
            # Cargar todas, incluyendo anuladas (para editar ingresos con órdenes anuladas)
            ordenes = db.query(OrdenDeCompra).all()
        # Forzar carga de detalles para cada orden
        for orden in ordenes:
            _ = orden.detalles
        return ordenes

    def get_by_id(self, db: Session, orden_id: int) -> Optional[OrdenDeCompra]:
        orden = db.query(OrdenDeCompra).filter(OrdenDeCompra.id_orden == orden_id, OrdenDeCompra.anulado == False).first()
        if orden:
            # Forzar carga de detalles
            _ = orden.detalles
        return orden

    def create(self, db: Session, orden: OrdenDeCompraCreate) -> OrdenDeCompra:
        orden_data = orden.model_dump(exclude={'detalles'})
        db_orden = OrdenDeCompra(**orden_data)

        db.add(db_orden)
        db.flush()

        for detalle_data in orden.detalles:
            db_detalle = OrdenDeCompraDetalle(**detalle_data.model_dump(), id_orden=db_orden.id_orden)
            db.add(db_detalle)

        db.commit()
        db.refresh(db_orden)
        # Forzar carga de detalles
        _ = db_orden.detalles
        return db_orden

    def update(self, db: Session, orden_id: int, orden: OrdenDeCompraUpdate) -> Optional[OrdenDeCompra]:
        db_orden = self.get_by_id(db, orden_id)
        if db_orden:
            update_data = orden.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                if key != "detalles":
                    setattr(db_orden, key, value)

            if "detalles" in update_data and update_data["detalles"] is not None:
                db.query(OrdenDeCompraDetalle).filter(OrdenDeCompraDetalle.id_orden == orden_id).delete()
                for detalle_data in orden.detalles:
                    db_detalle = OrdenDeCompraDetalle(**detalle_data.model_dump(), id_orden=orden_id)
                    db.add(db_detalle)

            db.commit()
            db.refresh(db_orden)
            # Forzar carga de detalles
            _ = db_orden.detalles
        return db_orden

    def delete(self, db: Session, orden_id: int) -> bool:
        db_orden = self.get_by_id(db, orden_id)
        if db_orden:
            db_orden.anulado = True
            db.commit()
            return True
        return False
    
    # ==================== SUGERENCIAS DE COMPRA (FC-10) ====================
    
    def obtener_stock_actual_insumos(self, db: Session) -> List[Dict[str, Any]]:
        """Obtiene el stock actual de todos los insumos activos."""
        from modules.insumo.model import Insumo
        from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProductoDetalle
        
        resultado = db.query(
            Insumo.id_insumo,
            Insumo.codigo,
            Insumo.nombre,
            Insumo.unidad_medida,
            Insumo.stock_minimo,
            Insumo.categoria,
            func.coalesce(func.sum(IngresoProductoDetalle.cantidad_restante), 0).label('stock_actual')
        ).outerjoin(
            IngresoProductoDetalle, Insumo.id_insumo == IngresoProductoDetalle.id_insumo
        ).filter(
            Insumo.anulado == False
        ).group_by(
            Insumo.id_insumo,
            Insumo.codigo,
            Insumo.nombre,
            Insumo.unidad_medida,
            Insumo.stock_minimo,
            Insumo.categoria
        ).all()
        
        return [
            {
                'id_insumo': r.id_insumo,
                'codigo': r.codigo,
                'nombre': r.nombre,
                'unidad_medida': str(r.unidad_medida.value) if r.unidad_medida else '',
                'stock_minimo': Decimal(str(r.stock_minimo or 0)),
                'stock_actual': Decimal(str(r.stock_actual or 0)),
                'categoria': str(r.categoria.value) if r.categoria else None
            }
            for r in resultado
        ]
    
    def obtener_consumo_promedio_insumos(
        self, 
        db: Session, 
        dias: int = 30
    ) -> Dict[int, Decimal]:
        """Obtiene el consumo promedio diario de insumos en los últimos N días."""
        from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
        
        fecha_inicio = date.today() - timedelta(days=dias)
        
        resultado = db.query(
            MovimientoInsumo.id_insumo,
            func.sum(MovimientoInsumo.cantidad).label('consumo_total')
        ).filter(
            MovimientoInsumo.anulado == False,
            MovimientoInsumo.tipo_movimiento == 'SALIDA',
            func.date(MovimientoInsumo.fecha_movimiento) >= fecha_inicio
        ).group_by(
            MovimientoInsumo.id_insumo
        ).all()
        
        # Convertir a diccionario con consumo diario promedio
        consumo_diario = {}
        for r in resultado:
            consumo_total = Decimal(str(r.consumo_total or 0))
            consumo_diario[r.id_insumo] = consumo_total / Decimal(str(dias))
        
        return consumo_diario
    
    def obtener_cantidad_por_vencer(
        self, 
        db: Session, 
        dias_limite: int = 7
    ) -> Dict[int, Decimal]:
        """Obtiene la cantidad de cada insumo que vence en los próximos N días."""
        from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProductoDetalle
        from modules.insumo.model import Insumo
        
        fecha_limite = date.today() + timedelta(days=dias_limite)
        
        resultado = db.query(
            IngresoProductoDetalle.id_insumo,
            func.sum(IngresoProductoDetalle.cantidad_restante).label('cantidad_por_vencer')
        ).join(
            Insumo, IngresoProductoDetalle.id_insumo == Insumo.id_insumo
        ).filter(
            IngresoProductoDetalle.cantidad_restante > 0,
            IngresoProductoDetalle.fecha_vencimiento <= fecha_limite,
            IngresoProductoDetalle.fecha_vencimiento >= date.today(),
            Insumo.perecible == True
        ).group_by(
            IngresoProductoDetalle.id_insumo
        ).all()
        
        return {r.id_insumo: Decimal(str(r.cantidad_por_vencer or 0)) for r in resultado}
    
    def obtener_ultimo_precio_insumos(self, db: Session) -> Dict[int, Decimal]:
        """Obtiene el último precio de compra de cada insumo."""
        from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProducto, IngresoProductoDetalle
        
        # Subquery para obtener el último ingreso por insumo
        subquery = db.query(
            IngresoProductoDetalle.id_insumo,
            func.max(IngresoProductoDetalle.id_ingreso_detalle).label('ultimo_id')
        ).group_by(
            IngresoProductoDetalle.id_insumo
        ).subquery()
        
        resultado = db.query(
            IngresoProductoDetalle.id_insumo,
            IngresoProductoDetalle.precio_unitario
        ).join(
            subquery, IngresoProductoDetalle.id_ingreso_detalle == subquery.c.ultimo_id
        ).all()
        
        return {r.id_insumo: Decimal(str(r.precio_unitario or 0)) for r in resultado}
    
    def obtener_proveedor_por_insumo(self, db: Session) -> Dict[int, Dict[str, Any]]:
        """Obtiene el proveedor del último ingreso de cada insumo."""
        from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProducto, IngresoProductoDetalle
        from modules.proveedores.model import Proveedor
        
        # Subquery para obtener el último ingreso por insumo
        subquery = db.query(
            IngresoProductoDetalle.id_insumo,
            func.max(IngresoProducto.id_ingreso).label('ultimo_ingreso')
        ).join(
            IngresoProducto, IngresoProductoDetalle.id_ingreso == IngresoProducto.id_ingreso
        ).group_by(
            IngresoProductoDetalle.id_insumo
        ).subquery()
        
        resultado = db.query(
            IngresoProductoDetalle.id_insumo,
            Proveedor.id_proveedor,
            Proveedor.nombre,
            Proveedor.email_contacto,
            Proveedor.numero_contacto
        ).join(
            IngresoProducto, IngresoProductoDetalle.id_ingreso == IngresoProducto.id_ingreso
        ).join(
            subquery, and_(
                IngresoProductoDetalle.id_insumo == subquery.c.id_insumo,
                IngresoProducto.id_ingreso == subquery.c.ultimo_ingreso
            )
        ).join(
            Proveedor, IngresoProducto.id_proveedor == Proveedor.id_proveedor
        ).filter(
            Proveedor.anulado == False
        ).all()
        
        return {
            r.id_insumo: {
                'id_proveedor': r.id_proveedor,
                'nombre': r.nombre,
                'email': r.email_contacto,
                'telefono': r.numero_contacto
            }
            for r in resultado
        }
    
    def obtener_proveedor_por_id(self, db: Session, id_proveedor: int) -> Optional[Dict[str, Any]]:
        """Obtiene información de un proveedor por ID."""
        from modules.proveedores.model import Proveedor
        
        proveedor = db.query(Proveedor).filter(
            Proveedor.id_proveedor == id_proveedor,
            Proveedor.anulado == False
        ).first()
        
        if proveedor:
            return {
                'id_proveedor': proveedor.id_proveedor,
                'nombre': proveedor.nombre,
                'email': proveedor.email_contacto,
                'telefono': proveedor.numero_contacto,
                'ruc': proveedor.ruc_dni,
                'direccion': proveedor.direccion_fiscal
            }
        return None
    
    def generar_numero_orden(self, db: Session) -> str:
        """Genera un número de orden único."""
        from datetime import datetime
        
        # Contar órdenes del día
        hoy = date.today()
        count = db.query(func.count(OrdenDeCompra.id_orden)).filter(
            func.date(OrdenDeCompra.fecha_orden) == hoy
        ).scalar() or 0
        
        return f"OC-{hoy.strftime('%Y%m%d')}-{str(count + 1).zfill(4)}"

