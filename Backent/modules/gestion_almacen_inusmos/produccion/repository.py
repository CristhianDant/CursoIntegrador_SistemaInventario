from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from decimal import Decimal
import datetime
from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
from enums.tipo_movimiento import TipoMovimientoEnum


class ProduccionRepository:
    """
    Repository para operaciones de producción.
    Usa raw SQL para facilitar modificaciones futuras.
    """

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
            ultimo_numero = int(ultimo_movimiento.numero_movimiento.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        return f"{prefijo}{nuevo_numero:05d}"

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
