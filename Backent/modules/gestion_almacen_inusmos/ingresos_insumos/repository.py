from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, text, func
from decimal import Decimal
import datetime
from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProducto, IngresoProductoDetalle
from modules.gestion_almacen_inusmos.ingresos_insumos.schemas import IngresoProductoCreate, IngresoProductoUpdate
from modules.gestion_almacen_inusmos.ingresos_insumos.repository_interface import IngresoProductoRepositoryInterface
from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
from enums.tipo_movimiento import TipoMovimientoEnum

class IngresoProductoRepository(IngresoProductoRepositoryInterface):
    def get_all(self, db: Session) -> List[IngresoProducto]:
        ingresos = db.query(IngresoProducto).filter(IngresoProducto.anulado == False).all()
        # Forzar carga de detalles
        for ingreso in ingresos:
            _ = ingreso.detalles
        return ingresos

    def get_by_id(self, db: Session, ingreso_id: int) -> Optional[IngresoProducto]:
        ingreso = db.query(IngresoProducto).filter(IngresoProducto.id_ingreso == ingreso_id, IngresoProducto.anulado == False).first()
        if ingreso:
            # Forzar carga de detalles
            _ = ingreso.detalles
        return ingreso

    def _generar_numero_movimiento(self, db: Session) -> str:
        """
        Genera un número de movimiento único con formato: MOV-YYYYMM-XXXXX
        Ejemplo: MOV-202511-00001
        """
        fecha_actual = datetime.datetime.now()
        prefijo = f"MOV-{fecha_actual.strftime('%Y%m')}-"
        
        # Obtener el último número de movimiento del mes actual
        ultimo_movimiento = db.query(MovimientoInsumo).filter(
            MovimientoInsumo.numero_movimiento.like(f"{prefijo}%")
        ).order_by(desc(MovimientoInsumo.numero_movimiento)).first()
        
        if ultimo_movimiento:
            # Extraer el número secuencial y aumentar en 1
            ultimo_numero = int(ultimo_movimiento.numero_movimiento.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        return f"{prefijo}{nuevo_numero:05d}"

    def create(self, db: Session, ingreso: IngresoProductoCreate) -> IngresoProducto:
        ingreso_data = ingreso.model_dump(exclude={'detalles'})
        db_ingreso = IngresoProducto(**ingreso_data)

        db.add(db_ingreso)
        db.flush()  # Obtener id_ingreso

        detalles_creados = []
        for detalle_data in ingreso.detalles:
            db_detalle = IngresoProductoDetalle(**detalle_data.model_dump(), id_ingreso=db_ingreso.id_ingreso)
            db.add(db_detalle)
            db.flush()  # Obtener id_ingreso_detalle para el movimiento
            detalles_creados.append(db_detalle)

        # Crear movimientos de ENTRADA para cada lote (detalle) - Actualiza el Kardex
        for db_detalle in detalles_creados:
            numero_movimiento = self._generar_numero_movimiento(db)
            
            movimiento = MovimientoInsumo(
                numero_movimiento=numero_movimiento,
                id_insumo=db_detalle.id_insumo,
                id_lote=db_detalle.id_ingreso_detalle,
                tipo_movimiento=TipoMovimientoEnum.ENTRADA.value,
                motivo="COMPRA",
                cantidad=db_detalle.cantidad_ingresada,
                stock_anterior_lote=Decimal('0'),  # Lote nuevo, stock anterior es 0
                stock_nuevo_lote=db_detalle.cantidad_restante,
                fecha_movimiento=datetime.datetime.now(),
                id_user=db_ingreso.id_user,
                id_documento_origen=db_ingreso.id_ingreso,
                tipo_documento_origen="INGRESO",
                observaciones=f"Entrada automática por ingreso {db_ingreso.numero_ingreso}",
                anulado=False
            )
            db.add(movimiento)

        db.commit()
        db.refresh(db_ingreso)
        # Forzar carga de detalles
        _ = db_ingreso.detalles
        return db_ingreso

    def update(self, db: Session, ingreso_id: int, ingreso: IngresoProductoUpdate) -> Optional[IngresoProducto]:
        db_ingreso = self.get_by_id(db, ingreso_id)
        if db_ingreso:
            update_data = ingreso.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                if key != "detalles":
                    setattr(db_ingreso, key, value)

            if "detalles" in update_data and update_data["detalles"] is not None:
                db.query(IngresoProductoDetalle).filter(IngresoProductoDetalle.id_ingreso == ingreso_id).delete()
                for detalle_data in ingreso.detalles:
                    db_detalle = IngresoProductoDetalle(**detalle_data.model_dump(), id_ingreso=ingreso_id)
                    db.add(db_detalle)

            db.commit()
            db.refresh(db_ingreso)
            # Forzar carga de detalles
            _ = db_ingreso.detalles
        return db_ingreso

    def delete(self, db: Session, ingreso_id: int) -> bool:
        db_ingreso = self.get_by_id(db, ingreso_id)
        if db_ingreso:
            db_ingreso.anulado = True
            db.commit()
            return True
        return False

    def get_lotes_fefo(self, db: Session, id_insumo: int) -> List[IngresoProductoDetalle]:
        """Obtiene todos los lotes (ingresos_detalle) de un insumo ordenados por FEFO
        Ordenamiento: cantidad_restante DESC (disponibilidad), fecha_vencimiento ASC (FEFO)
        Solo retorna lotes con cantidad_restante > 0
        """
        return db.query(IngresoProductoDetalle).filter(
            IngresoProductoDetalle.id_insumo == id_insumo,
            IngresoProductoDetalle.cantidad_restante > 0
        ).order_by(
            desc(IngresoProductoDetalle.cantidad_restante),
            asc(IngresoProductoDetalle.fecha_vencimiento)
        ).all()

    def get_lotes_fefo_con_proveedor(self, db: Session, id_insumo: int) -> List[dict]:
        """
        Obtiene todos los lotes de un insumo con información del proveedor e ingreso.
        Ordenados por FEFO (fecha_vencimiento ASC, lotes sin vencimiento al final).
        Solo retorna lotes con cantidad_restante > 0.
        
        Usa raw SQL para facilitar modificaciones futuras.
        
        Columnas retornadas:
        - id_ingreso_detalle, id_ingreso, cantidad_ingresada, cantidad_restante
        - precio_unitario, subtotal, fecha_vencimiento
        - numero_ingreso, fecha_ingreso (del ingreso padre)
        - nombre_proveedor (del proveedor)
        """
        query = text("""
            SELECT 
                iid.id_ingreso_detalle,
                iid.id_ingreso,
                iid.cantidad_ingresada,
                iid.cantidad_restante,
                iid.precio_unitario,
                iid.subtotal,
                iid.fecha_vencimiento,
                ii.numero_ingreso,
                ii.fecha_ingreso,
                p.nombre AS nombre_proveedor
            FROM ingresos_insumos_detalle iid
            INNER JOIN ingresos_insumos ii ON iid.id_ingreso = ii.id_ingreso
            INNER JOIN proveedores p ON ii.id_proveedor = p.id_proveedor
            WHERE iid.id_insumo = :id_insumo
              AND iid.cantidad_restante > 0
              AND ii.anulado = false
            ORDER BY 
                CASE WHEN iid.fecha_vencimiento IS NULL THEN 1 ELSE 0 END,
                iid.fecha_vencimiento ASC
        """)
        
        result = db.execute(query, {"id_insumo": id_insumo})
        rows = result.fetchall()
        
        # Convertir rows a lista de diccionarios
        lotes = []
        for row in rows:
            lotes.append({
                "id_ingreso_detalle": row.id_ingreso_detalle,
                "id_ingreso": row.id_ingreso,
                "cantidad_ingresada": row.cantidad_ingresada,
                "cantidad_restante": row.cantidad_restante,
                "precio_unitario": row.precio_unitario,
                "subtotal": row.subtotal,
                "fecha_vencimiento": row.fecha_vencimiento,
                "numero_ingreso": row.numero_ingreso,
                "fecha_ingreso": row.fecha_ingreso,
                "nombre_proveedor": row.nombre_proveedor
            })
        
        return lotes

