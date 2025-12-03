from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, text, func
from decimal import Decimal
import datetime
from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProducto, IngresoProductoDetalle
from modules.gestion_almacen_inusmos.ingresos_insumos.schemas import IngresoProductoCreate, IngresoProductoUpdate
from modules.gestion_almacen_inusmos.ingresos_insumos.repository_interface import IngresoProductoRepositoryInterface
from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
from modules.orden_de_compra.model import OrdenDeCompra
from enums.tipo_movimiento import TipoMovimientoEnum
from enums.estado import EstadoEnum

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

    def _crear_movimientos_entrada(self, db: Session, db_ingreso: IngresoProducto, detalles: List[IngresoProductoDetalle]):
        """
        Crea movimientos de ENTRADA para los detalles del ingreso.
        Solo se llama cuando el ingreso pasa a estado COMPLETADO.
        """
        for db_detalle in detalles:
            # Verificar si ya existe un movimiento para este detalle (evitar duplicados)
            movimiento_existente = db.query(MovimientoInsumo).filter(
                MovimientoInsumo.id_lote == db_detalle.id_ingreso_detalle,
                MovimientoInsumo.tipo_movimiento == TipoMovimientoEnum.ENTRADA.value,
                MovimientoInsumo.anulado == False
            ).first()
            
            if not movimiento_existente:
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

    def _actualizar_estado_orden_compra(self, db: Session, db_ingreso: IngresoProducto):
        """
        Actualiza el estado de la orden de compra asociada cuando el ingreso se completa.
        Si la orden tiene un ingreso completado, pasa a COMPLETADO.
        """
        if not db_ingreso.id_orden_compra:
            return  # No hay orden de compra asociada
        
        orden = db.query(OrdenDeCompra).filter(
            OrdenDeCompra.id_orden == db_ingreso.id_orden_compra,
            OrdenDeCompra.anulado == False
        ).first()
        
        if orden and str(orden.estado).upper() in ['PENDIENTE', 'APROBADO', 'ESTADOENUM.PENDIENTE', 'ESTADOENUM.APROBADO']:
            # Actualizar la orden de compra a COMPLETADO
            orden.estado = 'COMPLETADO'
            db.add(orden)

    def create(self, db: Session, ingreso: IngresoProductoCreate) -> IngresoProducto:
        ingreso_data = ingreso.model_dump(exclude={'detalles'})
        db_ingreso = IngresoProducto(**ingreso_data)

        db.add(db_ingreso)
        db.flush()  # Obtener id_ingreso

        # Determinar si el ingreso está COMPLETADO para asignar cantidad_restante
        es_completado = str(db_ingreso.estado).upper() in ['COMPLETADO', 'ESTADOENUM.COMPLETADO']

        detalles_creados = []
        for detalle_data in ingreso.detalles:
            detalle_dict = detalle_data.model_dump()
            # Si es PENDIENTE, cantidad_restante = 0 (no afecta stock)
            # Si es COMPLETADO, cantidad_restante = cantidad_ingresada
            if es_completado:
                detalle_dict['cantidad_restante'] = detalle_dict.get('cantidad_ingresada', 0)
            else:
                detalle_dict['cantidad_restante'] = Decimal('0')
            
            db_detalle = IngresoProductoDetalle(**detalle_dict, id_ingreso=db_ingreso.id_ingreso)
            db.add(db_detalle)
            db.flush()  # Obtener id_ingreso_detalle para el movimiento
            detalles_creados.append(db_detalle)

        # Crear movimientos de ENTRADA solo si está COMPLETADO
        if es_completado:
            self._crear_movimientos_entrada(db, db_ingreso, detalles_creados)
            # Actualizar estado de la orden de compra asociada
            self._actualizar_estado_orden_compra(db, db_ingreso)

        db.commit()
        db.refresh(db_ingreso)
        # Forzar carga de detalles
        _ = db_ingreso.detalles
        return db_ingreso

    def update(self, db: Session, ingreso_id: int, ingreso: IngresoProductoUpdate) -> Optional[IngresoProducto]:
        db_ingreso = self.get_by_id(db, ingreso_id)
        if db_ingreso:
            update_data = ingreso.model_dump(exclude_unset=True)
            
            # Guardar estado anterior para detectar cambio PENDIENTE -> COMPLETADO
            estado_anterior = str(db_ingreso.estado).upper()

            for key, value in update_data.items():
                if key != "detalles":
                    setattr(db_ingreso, key, value)

            # Detectar si cambió de PENDIENTE a COMPLETADO
            estado_nuevo = str(db_ingreso.estado).upper()
            cambio_a_completado = (
                estado_anterior in ['PENDIENTE', 'ESTADOENUM.PENDIENTE'] and 
                estado_nuevo in ['COMPLETADO', 'ESTADOENUM.COMPLETADO']
            )

            # Actualizar detalles existentes en lugar de eliminarlos y recrearlos
            # Esto evita violaciones de FK cuando hay movimientos referenciando los detalles
            if "detalles" in update_data and update_data["detalles"] is not None:
                detalles_existentes = {d.id_ingreso_detalle: d for d in db_ingreso.detalles}
                detalles_enviados_ids = set()
                detalles_actualizados = []
                
                for detalle_data in ingreso.detalles:
                    detalle_dict = detalle_data.model_dump()
                    id_detalle = detalle_dict.get('id_ingreso_detalle')
                    
                    if id_detalle and id_detalle in detalles_existentes:
                        # Actualizar detalle existente
                        db_detalle = detalles_existentes[id_detalle]
                        for key, value in detalle_dict.items():
                            if key != 'id_ingreso_detalle' and value is not None:
                                setattr(db_detalle, key, value)
                        
                        # Si cambia a COMPLETADO, actualizar cantidad_restante
                        if cambio_a_completado:
                            db_detalle.cantidad_restante = db_detalle.cantidad_ingresada
                        
                        detalles_enviados_ids.add(id_detalle)
                        detalles_actualizados.append(db_detalle)
                    else:
                        # Crear nuevo detalle
                        # Si está COMPLETADO, cantidad_restante = cantidad_ingresada
                        if estado_nuevo in ['COMPLETADO', 'ESTADOENUM.COMPLETADO']:
                            detalle_dict['cantidad_restante'] = detalle_dict.get('cantidad_ingresada', 0)
                        else:
                            detalle_dict['cantidad_restante'] = Decimal('0')
                        
                        # Remover id_ingreso_detalle si es None para evitar conflictos
                        if 'id_ingreso_detalle' in detalle_dict:
                            del detalle_dict['id_ingreso_detalle']
                        
                        nuevo_detalle = IngresoProductoDetalle(**detalle_dict, id_ingreso=ingreso_id)
                        db.add(nuevo_detalle)
                        db.flush()  # Obtener id para el movimiento
                        detalles_actualizados.append(nuevo_detalle)
                
                # Eliminar detalles que ya no están en la lista (solo si no tienen referencias)
                for id_existente, detalle_existente in detalles_existentes.items():
                    if id_existente not in detalles_enviados_ids:
                        # Verificar si tiene movimientos asociados
                        tiene_movimientos = db.query(MovimientoInsumo).filter(
                            MovimientoInsumo.id_lote == id_existente
                        ).first() is not None
                        
                        if not tiene_movimientos:
                            db.delete(detalle_existente)
                        # Si tiene movimientos, no se puede eliminar - mantener el detalle

                # Si cambió a COMPLETADO, crear movimientos de entrada
                if cambio_a_completado:
                    self._crear_movimientos_entrada(db, db_ingreso, detalles_actualizados)
                    # Actualizar estado de la orden de compra asociada
                    self._actualizar_estado_orden_compra(db, db_ingreso)

            elif cambio_a_completado:
                # No se enviaron detalles pero cambió a COMPLETADO
                # Actualizar cantidad_restante de detalles existentes y crear movimientos
                for detalle in db_ingreso.detalles:
                    detalle.cantidad_restante = detalle.cantidad_ingresada
                self._crear_movimientos_entrada(db, db_ingreso, db_ingreso.detalles)
                # Actualizar estado de la orden de compra asociada
                self._actualizar_estado_orden_compra(db, db_ingreso)

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

