from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
import datetime
from datetime import date
from modules.gestion_almacen_productos.ventas.repository_interface import VentasRepositoryInterface


class VentasRepository(VentasRepositoryInterface):
    """
    Repository para operaciones de ventas.
    Usa raw SQL para facilitar modificaciones futuras.
    """

    def generar_numero_venta(self, db: Session) -> str:
        """
        Genera un número de venta único con formato: VENTA-YYYYMM-N
        Ejemplo: VENTA-202511-1, VENTA-202511-2
        """
        fecha_actual = datetime.datetime.now()
        prefijo = f"VENTA-{fecha_actual.strftime('%Y%m')}-"
        
        query = text("""
            SELECT numero_venta 
            FROM ventas 
            WHERE numero_venta LIKE :prefijo
            ORDER BY id_venta DESC
            LIMIT 1
        """)
        
        result = db.execute(query, {"prefijo": f"{prefijo}%"})
        ultima_venta = result.fetchone()
        
        if ultima_venta:
            ultimo_numero = int(ultima_venta.numero_venta.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        
        return f"{prefijo}{nuevo_numero}"

    def generar_numero_movimiento_productos_terminados(self, db: Session) -> str:
        """
        Genera un número de movimiento único para movimiento_productos_terminados.
        Formato: MPT-YYYYMM-NNNNN
        Ejemplo: MPT-202511-00001
        """
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

        return f"{prefijo}{nuevo_numero:05d}"

    def crear_venta(
        self, 
        db: Session, 
        numero_venta: str,
        total: Decimal,
        metodo_pago: str,
        id_user: int,
        observaciones: Optional[str]
    ) -> Dict[str, Any]:
        """Crea un registro de venta y retorna datos básicos."""
        query = text("""
            INSERT INTO ventas (
                numero_venta, 
                fecha_venta, 
                total, 
                metodo_pago, 
                id_user, 
                observaciones, 
                anulado
            )
            VALUES (
                :numero_venta, 
                :fecha_venta, 
                :total, 
                :metodo_pago, 
                :id_user, 
                :observaciones, 
                false
            )
            RETURNING id_venta, numero_venta, fecha_venta
        """)
        
        result = db.execute(query, {
            "numero_venta": numero_venta,
            "fecha_venta": datetime.datetime.now(),
            "total": float(total),
            "metodo_pago": metodo_pago,
            "id_user": id_user,
            "observaciones": observaciones
        })
        
        row = result.fetchone()
        return {
            "id_venta": row.id_venta,
            "numero_venta": row.numero_venta,
            "fecha_venta": row.fecha_venta
        }

    def crear_detalle_venta(
        self,
        db: Session,
        id_venta: int,
        id_producto: int,
        cantidad: Decimal,
        precio_unitario: Decimal,
        descuento_porcentaje: Decimal,
        subtotal: Decimal
    ) -> int:
        """Crea un detalle de venta y retorna el id_detalle."""
        query = text("""
            INSERT INTO venta_detalles (
                id_venta,
                id_producto,
                cantidad,
                precio_unitario,
                descuento_porcentaje,
                subtotal
            )
            VALUES (
                :id_venta,
                :id_producto,
                :cantidad,
                :precio_unitario,
                :descuento_porcentaje,
                :subtotal
            )
            RETURNING id_detalle
        """)
        
        result = db.execute(query, {
            "id_venta": id_venta,
            "id_producto": id_producto,
            "cantidad": float(cantidad),
            "precio_unitario": float(precio_unitario),
            "descuento_porcentaje": float(descuento_porcentaje),
            "subtotal": float(subtotal)
        })
        
        row = result.fetchone()
        return row.id_detalle if row else None

    def get_stock_producto(self, db: Session, id_producto: int) -> Decimal:
        """Obtiene el stock actual de un producto terminado."""
        query = text("""
            SELECT stock_actual
            FROM productos_terminados
            WHERE id_producto = :id_producto
              AND anulado = false
        """)
        
        result = db.execute(query, {"id_producto": id_producto})
        row = result.fetchone()
        return Decimal(str(row.stock_actual)) if row else Decimal('0')

    def descontar_stock_producto(
        self, 
        db: Session, 
        id_producto: int, 
        cantidad: Decimal
    ) -> Decimal:
        """Descuenta stock de un producto y retorna el nuevo stock."""
        query = text("""
            UPDATE productos_terminados
            SET stock_actual = stock_actual - :cantidad
            WHERE id_producto = :id_producto
            RETURNING stock_actual
        """)
        
        result = db.execute(query, {
            "cantidad": float(cantidad),
            "id_producto": id_producto
        })
        
        row = result.fetchone()
        return Decimal(str(row.stock_actual)) if row else Decimal('0')

    def incrementar_stock_producto(
        self,
        db: Session,
        id_producto: int,
        cantidad: Decimal
    ) -> Decimal:
        """Incrementa stock de un producto y retorna el nuevo stock."""
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

    def crear_movimiento_salida(
        self,
        db: Session,
        id_producto: int,
        cantidad: Decimal,
        id_user: int,
        id_venta: int,
        numero_venta: str
    ):
        """Crea un movimiento de SALIDA en movimiento_productos_terminados."""
        numero_movimiento = self.generar_numero_movimiento_productos_terminados(db)

        query = text("""
            INSERT INTO movimiento_productos_terminados (
                numero_movimiento,
                id_producto,
                tipo_movimiento,
                motivo,
                cantidad,
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
                'SALIDA',
                'VENTA',
                :cantidad,
                :fecha_movimiento,
                :id_user,
                :id_venta,
                'VENTA',
                :observaciones,
                false
            )
        """)

        db.execute(query, {
            "numero_movimiento": numero_movimiento,
            "id_producto": id_producto,
            "cantidad": float(cantidad),
            "fecha_movimiento": datetime.datetime.now(),
            "id_user": id_user,
            "id_venta": id_venta,
            "observaciones": f"Salida por venta {numero_venta}"
        })

    def crear_movimiento_entrada_compensacion(
        self,
        db: Session,
        id_producto: int,
        cantidad: Decimal,
        id_user: int,
        id_venta: int,
        numero_venta: str
    ):
        """Crea un movimiento de ENTRADA por anulación de venta."""
        numero_movimiento = self.generar_numero_movimiento_productos_terminados(db)

        query = text("""
            INSERT INTO movimiento_productos_terminados (
                numero_movimiento,
                id_producto,
                tipo_movimiento,
                motivo,
                cantidad,
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
                'ANULACION_VENTA',
                :cantidad,
                :fecha_movimiento,
                :id_user,
                :id_venta,
                'VENTA',
                :observaciones,
                false
            )
        """)

        db.execute(query, {
            "numero_movimiento": numero_movimiento,
            "id_producto": id_producto,
            "cantidad": float(cantidad),
            "fecha_movimiento": datetime.datetime.now(),
            "id_user": id_user,
            "id_venta": id_venta,
            "observaciones": f"Entrada por anulación de venta {numero_venta}"
        })

    def get_producto_info(self, db: Session, id_producto: int) -> Optional[Dict[str, Any]]:
        """Obtiene información de un producto terminado."""
        query = text("""
            SELECT 
                id_producto,
                codigo_producto,
                nombre,
                descripcion,
                stock_actual,
                precio_venta,
                anulado
            FROM productos_terminados
            WHERE id_producto = :id_producto
              AND anulado = false
        """)
        
        result = db.execute(query, {"id_producto": id_producto})
        row = result.fetchone()
        
        if not row:
            return None
        
        return {
            "id_producto": row.id_producto,
            "codigo_producto": row.codigo_producto,
            "nombre": row.nombre,
            "descripcion": row.descripcion,
            "stock_actual": Decimal(str(row.stock_actual)),
            "precio_venta": Decimal(str(row.precio_venta)),
            "anulado": row.anulado
        }

    def get_venta_por_id(self, db: Session, id_venta: int) -> Optional[Dict[str, Any]]:
        """Obtiene una venta por ID con sus detalles."""
        # Obtener datos de la venta
        query_venta = text("""
            SELECT 
                v.id_venta,
                v.numero_venta,
                v.fecha_venta,
                v.total,
                v.metodo_pago,
                v.id_user,
                u.nombre AS nombre_usuario,
                v.observaciones,
                v.anulado
            FROM ventas v
            INNER JOIN usuario u ON v.id_user = u.id_user
            WHERE v.id_venta = :id_venta
        """)
        
        result_venta = db.execute(query_venta, {"id_venta": id_venta})
        venta = result_venta.fetchone()
        
        if not venta:
            return None
        
        # Obtener detalles de la venta
        query_detalles = text("""
            SELECT 
                vd.id_detalle,
                vd.id_producto,
                pt.nombre AS nombre_producto,
                vd.cantidad,
                vd.precio_unitario,
                vd.descuento_porcentaje,
                vd.subtotal
            FROM venta_detalles vd
            INNER JOIN productos_terminados pt ON vd.id_producto = pt.id_producto
            WHERE vd.id_venta = :id_venta
        """)
        
        result_detalles = db.execute(query_detalles, {"id_venta": id_venta})
        detalles = result_detalles.fetchall()
        
        return {
            "id_venta": venta.id_venta,
            "numero_venta": venta.numero_venta,
            "fecha_venta": venta.fecha_venta,
            "total": Decimal(str(venta.total)),
            "metodo_pago": venta.metodo_pago,
            "id_user": venta.id_user,
            "nombre_usuario": venta.nombre_usuario,
            "observaciones": venta.observaciones,
            "anulado": venta.anulado,
            "detalles": [
                {
                    "id_detalle": det.id_detalle,
                    "id_producto": det.id_producto,
                    "nombre_producto": det.nombre_producto,
                    "cantidad": Decimal(str(det.cantidad)),
                    "precio_unitario": Decimal(str(det.precio_unitario)),
                    "descuento_porcentaje": Decimal(str(det.descuento_porcentaje)),
                    "subtotal": Decimal(str(det.subtotal))
                }
                for det in detalles
            ]
        }

    def get_ventas_del_dia(self, db: Session, fecha: date) -> List[Dict[str, Any]]:
        """Obtiene todas las ventas de un día específico."""
        query = text("""
            SELECT 
                v.id_venta,
                v.numero_venta,
                v.fecha_venta,
                v.total,
                v.metodo_pago,
                u.nombre AS nombre_usuario,
                v.anulado,
                COUNT(vd.id_detalle) AS cantidad_items
            FROM ventas v
            INNER JOIN usuario u ON v.id_user = u.id_user
            LEFT JOIN venta_detalles vd ON v.id_venta = vd.id_venta
            WHERE DATE(v.fecha_venta) = :fecha
            GROUP BY v.id_venta, v.numero_venta, v.fecha_venta, v.total, 
                     v.metodo_pago, u.nombre, v.anulado
            ORDER BY v.fecha_venta DESC
        """)
        
        result = db.execute(query, {"fecha": fecha})
        rows = result.fetchall()
        
        return [
            {
                "id_venta": row.id_venta,
                "numero_venta": row.numero_venta,
                "fecha_venta": row.fecha_venta,
                "total": Decimal(str(row.total)),
                "metodo_pago": row.metodo_pago,
                "nombre_usuario": row.nombre_usuario,
                "cantidad_items": row.cantidad_items,
                "anulado": row.anulado
            }
            for row in rows
        ]

    def get_productos_disponibles(self, db: Session) -> List[Dict[str, Any]]:
        """Obtiene productos con stock disponible para venta."""
        query = text("""
            SELECT 
                id_producto,
                codigo_producto,
                nombre,
                descripcion,
                stock_actual,
                precio_venta
            FROM productos_terminados
            WHERE stock_actual > 0
              AND anulado = false
            ORDER BY nombre ASC
        """)
        
        result = db.execute(query)
        rows = result.fetchall()
        
        return [
            {
                "id_producto": row.id_producto,
                "codigo_producto": row.codigo_producto,
                "nombre": row.nombre,
                "descripcion": row.descripcion,
                "stock_actual": Decimal(str(row.stock_actual)),
                "precio_venta": Decimal(str(row.precio_venta))
            }
            for row in rows
        ]

    def anular_venta(self, db: Session, id_venta: int) -> bool:
        """Marca una venta como anulada."""
        query = text("""
            UPDATE ventas
            SET anulado = true
            WHERE id_venta = :id_venta
            RETURNING id_venta
        """)
        
        result = db.execute(query, {"id_venta": id_venta})
        row = result.fetchone()
        return row is not None

    def get_ultima_produccion_producto(
        self, 
        db: Session, 
        id_producto: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene la fecha de la última producción de un producto."""
        query = text("""
            SELECT 
                p.id_produccion,
                p.fecha_produccion,
                p.cantidad_batch,
                r.rendimiento_producto_terminado
            FROM produccion p
            INNER JOIN recetas r ON p.id_receta = r.id_receta
            WHERE r.id_producto = :id_producto
              AND p.anulado = false
            ORDER BY p.fecha_produccion DESC
            LIMIT 1
        """)
        
        result = db.execute(query, {"id_producto": id_producto})
        row = result.fetchone()
        
        if not row:
            return None
        
        return {
            "id_produccion": row.id_produccion,
            "fecha_produccion": row.fecha_produccion,
            "cantidad_batch": Decimal(str(row.cantidad_batch)),
            "rendimiento_producto_terminado": Decimal(str(row.rendimiento_producto_terminado))
        }
