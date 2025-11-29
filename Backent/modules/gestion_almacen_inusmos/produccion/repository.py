from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from decimal import Decimal
import datetime
from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
from modules.gestion_almacen_inusmos.produccion.model import Produccion
from enums.tipo_movimiento import TipoMovimientoEnum


class ProduccionRepository:
    """
    Repository para operaciones de producción.
    Usa raw SQL para facilitar modificaciones futuras.
    """
    
    # Contador para números de movimiento en la sesión actual
    _numero_contador = {}

    def _generar_numero_movimiento(self, db: Session) -> str:
        """
        Genera un número de movimiento único con formato: MOV-YYYYMM-XXXXX
        Ejemplo: MOV-202511-00001
        """
        fecha_actual = datetime.datetime.now()
        prefijo = f"MOV-{fecha_actual.strftime('%Y%m')}-"
        
        # Usar contador por prefijo para asegurar unicidad en la sesión
        if prefijo not in self._numero_contador:
            # Obtener el máximo actual de la BD
            query = text("""
                SELECT COALESCE(MAX(CAST(SUBSTRING(numero_movimiento FROM LENGTH(:prefijo) + 1) AS INTEGER)), 0)
                FROM movimiento_insumos 
                WHERE numero_movimiento LIKE :prefijo_pattern
            """)
            
            result = db.execute(query, {
                "prefijo": prefijo,
                "prefijo_pattern": f"{prefijo}%"
            })
            max_bd = result.fetchone()[0]
            self._numero_contador[prefijo] = max_bd
        
        # Incrementar contador
        self._numero_contador[prefijo] += 1
        nuevo_numero = self._numero_contador[prefijo]
        
        return f"{prefijo}{nuevo_numero:05d}"

    def _reset_contador_movimientos(self):
        """Resetea el contador de números de movimiento"""
        self._numero_contador.clear()

    def get_receta_con_insumos(self, db: Session, id_receta: int) -> Dict[str, Any]:
        """
        Obtiene la receta con sus insumos requeridos.
        Retorna información de la receta y lista de insumos con cantidades.
        """
        # Obtener datos de la receta
        query_receta = text("""
            SELECT 
                r.id_receta,
                r.codigo_receta,
                r.nombre_receta,
                r.rendimiento_producto_terminado,
                r.estado,
                r.anulado
            FROM recetas r
            WHERE r.id_receta = :id_receta
              AND r.anulado = false
              AND r.estado = 'ACTIVA'
        """)
        
        result_receta = db.execute(query_receta, {"id_receta": id_receta})
        receta = result_receta.fetchone()
        
        if not receta:
            return None
        
        # Obtener insumos de la receta
        query_insumos = text("""
            SELECT 
                rd.id_receta_detalle,
                rd.id_insumo,
                rd.cantidad,
                rd.es_opcional,
                i.codigo AS codigo_insumo,
                i.nombre AS nombre_insumo,
                i.unidad_medida
            FROM recetas_detalle rd
            INNER JOIN insumo i ON rd.id_insumo = i.id_insumo
            WHERE rd.id_receta = :id_receta
              AND i.anulado = false
        """)
        
        result_insumos = db.execute(query_insumos, {"id_receta": id_receta})
        insumos = result_insumos.fetchall()
        
        return {
            "receta": {
                "id_receta": receta.id_receta,
                "codigo_receta": receta.codigo_receta,
                "nombre_receta": receta.nombre_receta,
                "rendimiento_producto_terminado": receta.rendimiento_producto_terminado
            },
            "insumos": [
                {
                    "id_insumo": ins.id_insumo,
                    "codigo_insumo": ins.codigo_insumo,
                    "nombre_insumo": ins.nombre_insumo,
                    "unidad_medida": ins.unidad_medida,
                    "cantidad_por_rendimiento": ins.cantidad,
                    "es_opcional": ins.es_opcional
                }
                for ins in insumos
            ]
        }

    def get_stock_disponible_insumo(self, db: Session, id_insumo: int) -> Decimal:
        """
        Obtiene el stock total disponible de un insumo.
        Suma de cantidad_restante de todos los lotes con stock > 0.
        """
        query = text("""
            SELECT COALESCE(SUM(iid.cantidad_restante), 0) AS stock_total
            FROM ingresos_insumos_detalle iid
            INNER JOIN ingresos_insumos ii ON iid.id_ingreso = ii.id_ingreso
            WHERE iid.id_insumo = :id_insumo
              AND iid.cantidad_restante > 0
              AND ii.anulado = false
        """)
        
        result = db.execute(query, {"id_insumo": id_insumo})
        row = result.fetchone()
        
        return Decimal(str(row.stock_total)) if row else Decimal('0')

    def get_lotes_fefo(self, db: Session, id_insumo: int) -> List[Dict[str, Any]]:
        """
        Obtiene los lotes de un insumo ordenados por FEFO.
        Solo lotes con cantidad_restante > 0.
        Ordenamiento: fecha_vencimiento ASC (NULL al final).
        """
        query = text("""
            SELECT 
                iid.id_ingreso_detalle,
                iid.id_ingreso,
                iid.id_insumo,
                iid.cantidad_restante,
                iid.precio_unitario,
                iid.fecha_vencimiento
            FROM ingresos_insumos_detalle iid
            INNER JOIN ingresos_insumos ii ON iid.id_ingreso = ii.id_ingreso
            WHERE iid.id_insumo = :id_insumo
              AND iid.cantidad_restante > 0
              AND ii.anulado = false
            ORDER BY 
                CASE WHEN iid.fecha_vencimiento IS NULL THEN 1 ELSE 0 END,
                iid.fecha_vencimiento ASC
        """)
        
        result = db.execute(query, {"id_insumo": id_insumo})
        rows = result.fetchall()
        
        return [
            {
                "id_ingreso_detalle": row.id_ingreso_detalle,
                "id_ingreso": row.id_ingreso,
                "id_insumo": row.id_insumo,
                "cantidad_restante": Decimal(str(row.cantidad_restante)),
                "precio_unitario": Decimal(str(row.precio_unitario)),
                "fecha_vencimiento": row.fecha_vencimiento
            }
            for row in rows
        ]

    def descontar_lote(self, db: Session, id_ingreso_detalle: int, cantidad_a_descontar: Decimal) -> Decimal:
        """
        Descuenta cantidad de un lote específico.
        Retorna la nueva cantidad_restante del lote.
        """
        query = text("""
            UPDATE ingresos_insumos_detalle
            SET cantidad_restante = cantidad_restante - :cantidad
            WHERE id_ingreso_detalle = :id_lote
            RETURNING cantidad_restante
        """)
        
        result = db.execute(query, {
            "cantidad": float(cantidad_a_descontar),
            "id_lote": id_ingreso_detalle
        })
        
        row = result.fetchone()
        return Decimal(str(row.cantidad_restante)) if row else Decimal('0')

    def crear_movimiento_salida(
        self, 
        db: Session, 
        id_insumo: int,
        id_lote: int,
        cantidad: Decimal,
        stock_anterior: Decimal,
        stock_nuevo: Decimal,
        id_user: int,
        id_documento_origen: int,
        observaciones: str
    ) -> MovimientoInsumo:
        """
        Crea un movimiento de SALIDA para el Kardex.
        """
        numero_movimiento = self._generar_numero_movimiento(db)
        
        movimiento = MovimientoInsumo(
            numero_movimiento=numero_movimiento,
            id_insumo=id_insumo,
            id_lote=id_lote,
            tipo_movimiento=TipoMovimientoEnum.SALIDA.value,
            motivo="PRODUCCION",
            cantidad=cantidad,  # Cantidad positiva, el tipo indica SALIDA
            stock_anterior_lote=stock_anterior,
            stock_nuevo_lote=stock_nuevo,
            fecha_movimiento=datetime.datetime.now(),
            id_user=id_user,
            id_documento_origen=id_documento_origen,
            tipo_documento_origen="PRODUCCION",
            observaciones=observaciones,
            anulado=False
        )
        
        db.add(movimiento)
        return movimiento

    def descontar_insumo_fefo(
        self, 
        db: Session, 
        id_insumo: int, 
        cantidad_requerida: Decimal,
        id_user: int,
        id_receta: int,
        nombre_receta: str
    ) -> int:
        """
        Descuenta la cantidad requerida de un insumo usando FEFO.
        Crea movimientos de SALIDA por cada lote afectado.
        Retorna el número de movimientos creados.
        
        IMPORTANTE: Esta función NO hace commit, para permitir
        que el service maneje la transacción completa.
        """
        lotes = self.get_lotes_fefo(db, id_insumo)
        cantidad_pendiente = cantidad_requerida
        movimientos_creados = 0
        
        for lote in lotes:
            if cantidad_pendiente <= 0:
                break
            
            stock_anterior = lote["cantidad_restante"]
            
            # Determinar cuánto descontar de este lote
            if stock_anterior >= cantidad_pendiente:
                cantidad_descontar = cantidad_pendiente
            else:
                cantidad_descontar = stock_anterior
            
            # Descontar del lote
            stock_nuevo = self.descontar_lote(
                db, 
                lote["id_ingreso_detalle"], 
                cantidad_descontar
            )
            
            # Crear movimiento de SALIDA
            self.crear_movimiento_salida(
                db=db,
                id_insumo=id_insumo,
                id_lote=lote["id_ingreso_detalle"],
                cantidad=cantidad_descontar,
                stock_anterior=stock_anterior,
                stock_nuevo=stock_nuevo,
                id_user=id_user,
                id_documento_origen=id_receta,
                observaciones=f"Salida por producción de receta: {nombre_receta}"
            )
            
            cantidad_pendiente -= cantidad_descontar
            movimientos_creados += 1
        
        return movimientos_creados

    # ============================================================
    # NUEVOS MÉTODOS PARA TABLA PRODUCCION
    # ============================================================

    def _generar_numero_produccion(self, db: Session) -> str:
        """
        Genera un número de producción único con formato: PROD-YYYYMM-N
        Ejemplo: PROD-202511-1, PROD-202511-2
        """
        fecha_actual = datetime.datetime.now()
        prefijo = f"PROD-{fecha_actual.strftime('%Y%m')}-"
        
        query = text("""
            SELECT numero_produccion 
            FROM produccion 
            WHERE numero_produccion LIKE :prefijo
            ORDER BY id_produccion DESC
            LIMIT 1
        """)
        
        result = db.execute(query, {"prefijo": f"{prefijo}%"})
        ultima_produccion = result.fetchone()
        
        if ultima_produccion:
            ultimo_numero = int(ultima_produccion.numero_produccion.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        return f"{prefijo}{nuevo_numero}"

    def crear_produccion(
        self, 
        db: Session, 
        id_receta: int, 
        cantidad_batch: Decimal, 
        id_user: int, 
        observaciones: str = None
    ) -> Dict[str, Any]:
        """
        Crea un registro en la tabla produccion.
        Retorna el id_produccion y numero_produccion generados.
        """
        numero_produccion = self._generar_numero_produccion(db)
        
        query = text("""
            INSERT INTO produccion (
                numero_produccion, 
                id_receta, 
                cantidad_batch, 
                fecha_produccion, 
                id_user, 
                observaciones, 
                anulado
            )
            VALUES (
                :numero_produccion, 
                :id_receta, 
                :cantidad_batch, 
                NOW(), 
                :id_user, 
                :observaciones, 
                false
            )
            RETURNING id_produccion, numero_produccion, fecha_produccion
        """)
        
        result = db.execute(query, {
            "numero_produccion": numero_produccion,
            "id_receta": id_receta,
            "cantidad_batch": float(cantidad_batch),
            "id_user": id_user,
            "observaciones": observaciones
        })
        
        row = result.fetchone()
        return {
            "id_produccion": row.id_produccion,
            "numero_produccion": row.numero_produccion,
            "fecha_produccion": row.fecha_produccion
        }

    def get_id_producto_de_receta(self, db: Session, id_receta: int) -> int:
        """
        Obtiene el id_producto asociado a una receta.
        """
        query = text("""
            SELECT id_producto
            FROM recetas
            WHERE id_receta = :id_receta
        """)
        
        result = db.execute(query, {"id_receta": id_receta})
        row = result.fetchone()
        return row.id_producto if row else None

    def incrementar_stock_producto_terminado(
        self, 
        db: Session, 
        id_producto: int, 
        cantidad: Decimal
    ) -> Decimal:
        """
        Incrementa el stock_actual del producto terminado.
        Retorna el nuevo stock.
        """
        query = text("""
            UPDATE productos_terminados
            SET stock_actual = stock_actual + :cantidad
            WHERE id_producto = :id_producto
            RETURNING stock_actual
        """)
        
        result = db.execute(query, {
            "cantidad": float(cantidad),
            "id_producto": id_producto
        })
        
        row = result.fetchone()
        return Decimal(str(row.stock_actual)) if row else Decimal('0')

    def crear_movimiento_producto_terminado(
        self,
        db: Session,
        id_producto: int,
        cantidad: Decimal,
        stock_anterior: Decimal,
        stock_nuevo: Decimal,
        id_user: int,
        id_produccion: int,
        observaciones: str
    ) -> int:
        """
        Crea un movimiento de ENTRADA en productos_terminados (Kardex).
        Retorna el id del movimiento creado.
        """
        # Generar número de movimiento para productos terminados
        fecha_actual = datetime.datetime.now()
        prefijo = f"MPT-{fecha_actual.strftime('%Y%m')}-"
        
        query_ultimo = text("""
            SELECT numero_movimiento 
            FROM movimiento_productos_terminados 
            WHERE numero_movimiento LIKE :prefijo
            ORDER BY id_movimiento DESC
            LIMIT 1
        """)
        
        result = db.execute(query_ultimo, {"prefijo": f"{prefijo}%"})
        ultimo = result.fetchone()
        
        if ultimo:
            ultimo_numero = int(ultimo.numero_movimiento.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        numero_movimiento = f"{prefijo}{nuevo_numero:05d}"
        
        query = text("""
            INSERT INTO movimiento_productos_terminados (
                numero_movimiento,
                id_producto,
                tipo_movimiento,
                motivo,
                cantidad,
                precio_venta,
                fecha_movimiento,
                id_user,
                id_documento_origen,
                tipo_documento_origen,
                observaciones,
                anulado
            )
            VALUES (
                :numero_movimiento,
                :id_producto,
                'ENTRADA',
                'PRODUCCION',
                :cantidad,
                0,
                NOW(),
                :id_user,
                :id_produccion,
                'PRODUCCION',
                :observaciones,
                false
            )
            RETURNING id_movimiento
        """)
        
        result = db.execute(query, {
            "numero_movimiento": numero_movimiento,
            "id_producto": id_producto,
            "cantidad": float(cantidad),
            "id_user": id_user,
            "id_produccion": id_produccion,
            "observaciones": observaciones
        })
        
        row = result.fetchone()
        return row.id_movimiento if row else None

    def get_stock_producto_terminado(self, db: Session, id_producto: int) -> Decimal:
        """
        Obtiene el stock actual de un producto terminado.
        """
        query = text("""
            SELECT stock_actual
            FROM productos_terminados
            WHERE id_producto = :id_producto
        """)
        
        result = db.execute(query, {"id_producto": id_producto})
        row = result.fetchone()
        return Decimal(str(row.stock_actual)) if row else Decimal('0')

    def get_historial_producciones(
        self, 
        db: Session, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de producciones con información de receta.
        Ordenado por fecha descendente.
        """
        query = text("""
            SELECT 
                p.id_produccion,
                p.numero_produccion,
                p.id_receta,
                r.codigo_receta,
                r.nombre_receta,
                pt.nombre AS nombre_producto,
                p.cantidad_batch,
                r.rendimiento_producto_terminado,
                (p.cantidad_batch * r.rendimiento_producto_terminado) AS cantidad_producida,
                p.fecha_produccion,
                p.id_user,
                u.nombre AS nombre_usuario,
                p.observaciones,
                p.anulado
            FROM produccion p
            INNER JOIN recetas r ON p.id_receta = r.id_receta
            INNER JOIN productos_terminados pt ON r.id_producto = pt.id_producto
            INNER JOIN usuario u ON p.id_user = u.id_user
            ORDER BY p.fecha_produccion DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = db.execute(query, {"limit": limit, "offset": offset})
        rows = result.fetchall()
        
        return [
            {
                "id_produccion": row.id_produccion,
                "numero_produccion": row.numero_produccion,
                "id_receta": row.id_receta,
                "codigo_receta": row.codigo_receta,
                "nombre_receta": row.nombre_receta,
                "nombre_producto": row.nombre_producto,
                "cantidad_batch": Decimal(str(row.cantidad_batch)),
                "rendimiento_producto_terminado": Decimal(str(row.rendimiento_producto_terminado)),
                "cantidad_producida": Decimal(str(row.cantidad_producida)),
                "fecha_produccion": row.fecha_produccion,
                "id_user": row.id_user,
                "nombre_usuario": row.nombre_usuario,
                "observaciones": row.observaciones,
                "anulado": row.anulado
            }
            for row in rows
        ]

    def get_trazabilidad_produccion(self, db: Session, id_produccion: int) -> Dict[str, Any]:
        """
        Obtiene la trazabilidad completa de una producción:
        - Datos de la producción
        - Receta utilizada
        - Lotes de insumos consumidos (movimientos de salida)
        - Producto terminado generado
        """
        # 1. Obtener datos de la producción
        query_produccion = text("""
            SELECT 
                p.id_produccion,
                p.numero_produccion,
                p.id_receta,
                r.codigo_receta,
                r.nombre_receta,
                r.id_producto,
                pt.nombre AS nombre_producto,
                p.cantidad_batch,
                r.rendimiento_producto_terminado,
                (p.cantidad_batch * r.rendimiento_producto_terminado) AS cantidad_producida,
                p.fecha_produccion,
                p.id_user,
                u.nombre AS nombre_usuario,
                p.observaciones,
                p.anulado
            FROM produccion p
            INNER JOIN recetas r ON p.id_receta = r.id_receta
            INNER JOIN productos_terminados pt ON r.id_producto = pt.id_producto
            INNER JOIN usuario u ON p.id_user = u.id_user
            WHERE p.id_produccion = :id_produccion
        """)
        
        result_prod = db.execute(query_produccion, {"id_produccion": id_produccion})
        produccion = result_prod.fetchone()
        
        if not produccion:
            return None
        
        # 2. Obtener movimientos de salida de insumos asociados a esta producción
        query_movimientos = text("""
            SELECT 
                mi.id_movimiento,
                mi.numero_movimiento,
                mi.id_insumo,
                i.codigo AS codigo_insumo,
                i.nombre AS nombre_insumo,
                i.unidad_medida,
                mi.id_lote,
                iid.fecha_vencimiento AS fecha_vencimiento_lote,
                mi.cantidad,
                mi.stock_anterior_lote,
                mi.stock_nuevo_lote,
                mi.fecha_movimiento
            FROM movimiento_insumos mi
            INNER JOIN insumo i ON mi.id_insumo = i.id_insumo
            LEFT JOIN ingresos_insumos_detalle iid ON mi.id_lote = iid.id_ingreso_detalle
            WHERE mi.id_documento_origen = :id_produccion
              AND mi.tipo_documento_origen = 'PRODUCCION'
              AND mi.tipo_movimiento = 'SALIDA'
              AND mi.anulado = false
            ORDER BY mi.fecha_movimiento ASC
        """)
        
        result_mov = db.execute(query_movimientos, {"id_produccion": id_produccion})
        movimientos = result_mov.fetchall()
        
        # 3. Obtener movimiento de entrada del producto terminado
        query_mov_pt = text("""
            SELECT 
                mpt.id_movimiento,
                mpt.numero_movimiento,
                mpt.cantidad,
                mpt.fecha_movimiento
            FROM movimiento_productos_terminados mpt
            WHERE mpt.id_documento_origen = :id_produccion
              AND mpt.tipo_documento_origen = 'PRODUCCION'
              AND mpt.tipo_movimiento = 'ENTRADA'
              AND mpt.anulado = false
        """)
        
        result_mov_pt = db.execute(query_mov_pt, {"id_produccion": id_produccion})
        mov_producto = result_mov_pt.fetchone()
        
        return {
            "produccion": {
                "id_produccion": produccion.id_produccion,
                "numero_produccion": produccion.numero_produccion,
                "fecha_produccion": produccion.fecha_produccion,
                "cantidad_batch": Decimal(str(produccion.cantidad_batch)),
                "cantidad_producida": Decimal(str(produccion.cantidad_producida)),
                "usuario": produccion.nombre_usuario,
                "observaciones": produccion.observaciones,
                "anulado": produccion.anulado
            },
            "receta": {
                "id_receta": produccion.id_receta,
                "codigo_receta": produccion.codigo_receta,
                "nombre_receta": produccion.nombre_receta,
                "rendimiento_producto_terminado": Decimal(str(produccion.rendimiento_producto_terminado))
            },
            "producto_terminado": {
                "id_producto": produccion.id_producto,
                "nombre_producto": produccion.nombre_producto,
                "movimiento_entrada": {
                    "id_movimiento": mov_producto.id_movimiento if mov_producto else None,
                    "numero_movimiento": mov_producto.numero_movimiento if mov_producto else None,
                    "cantidad": Decimal(str(mov_producto.cantidad)) if mov_producto else None,
                    "fecha_movimiento": mov_producto.fecha_movimiento if mov_producto else None
                } if mov_producto else None
            },
            "insumos_consumidos": [
                {
                    "id_movimiento": mov.id_movimiento,
                    "numero_movimiento": mov.numero_movimiento,
                    "id_insumo": mov.id_insumo,
                    "codigo_insumo": mov.codigo_insumo,
                    "nombre_insumo": mov.nombre_insumo,
                    "unidad_medida": mov.unidad_medida,
                    "id_lote": mov.id_lote,
                    "fecha_vencimiento_lote": mov.fecha_vencimiento_lote,
                    "cantidad_consumida": Decimal(str(mov.cantidad)),
                    "stock_anterior_lote": Decimal(str(mov.stock_anterior_lote)) if mov.stock_anterior_lote else None,
                    "stock_nuevo_lote": Decimal(str(mov.stock_nuevo_lote)) if mov.stock_nuevo_lote else None,
                    "fecha_movimiento": mov.fecha_movimiento
                }
                for mov in movimientos
            ],
            "total_lotes_consumidos": len(movimientos)
        }