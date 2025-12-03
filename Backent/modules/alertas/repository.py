from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional, Tuple
from datetime import date, datetime
from decimal import Decimal

from .model import Notificacion, TipoAlerta, SemaforoEstado
from .repository_interface import AlertasRepositoryInterface


class AlertasRepository(AlertasRepositoryInterface):
    """Repositorio para operaciones de base de datos del módulo de alertas."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== NOTIFICACIONES CRUD ====================
    
    def crear_notificacion(self, notificacion: Notificacion) -> Notificacion:
        """Crea una nueva notificación."""
        self.db.add(notificacion)
        self.db.flush()
        return notificacion
    
    def crear_notificaciones_batch(self, notificaciones: List[Notificacion]) -> int:
        """Crea múltiples notificaciones en batch."""
        self.db.add_all(notificaciones)
        self.db.flush()
        return len(notificaciones)
    
    def obtener_notificacion_por_id(self, id_notificacion: int) -> Optional[Notificacion]:
        """Obtiene una notificación por su ID."""
        return self.db.query(Notificacion).filter(
            Notificacion.id_notificacion == id_notificacion
        ).first()
    
    def obtener_notificaciones_activas(
        self,
        tipo: Optional[TipoAlerta] = None,
        solo_no_leidas: bool = False,
        limit: int = 100
    ) -> List[Notificacion]:
        """Obtiene notificaciones activas con filtros opcionales."""
        from modules.insumo.model import Insumo
        
        query = self.db.query(
            Notificacion,
            Insumo.nombre.label('nombre_insumo'),
            Insumo.codigo.label('codigo_insumo')
        ).outerjoin(
            Insumo, Notificacion.id_insumo == Insumo.id_insumo
        ).filter(Notificacion.activa == True)
        
        if tipo:
            query = query.filter(Notificacion.tipo == tipo)
        
        if solo_no_leidas:
            query = query.filter(Notificacion.leida == False)
        
        results = query.order_by(Notificacion.fecha_creacion.desc()).limit(limit).all()
        
        # Attach the joined data to the Notificacion objects
        for notif, nombre_insumo, codigo_insumo in results:
            notif.nombre_insumo = nombre_insumo
            notif.codigo_insumo = codigo_insumo
        
        return [notif for notif, _, _ in results]
    
    def marcar_como_leida(self, id_notificacion: int) -> bool:
        """Marca una notificación como leída."""
        result = self.db.query(Notificacion).filter(
            Notificacion.id_notificacion == id_notificacion
        ).update({
            "leida": True,
            "fecha_lectura": datetime.now()
        })
        return result > 0
    
    def marcar_todas_como_leidas(self, tipo: Optional[TipoAlerta] = None) -> int:
        """Marca todas las notificaciones como leídas."""
        query = self.db.query(Notificacion).filter(
            Notificacion.activa == True,
            Notificacion.leida == False
        )
        
        if tipo:
            query = query.filter(Notificacion.tipo == tipo)
        
        return query.update({
            "leida": True,
            "fecha_lectura": datetime.now()
        })
    
    def desactivar_notificaciones_antiguas_por_insumo(
        self,
        id_insumo: int,
        tipo: TipoAlerta
    ) -> int:
        """Desactiva notificaciones anteriores del mismo tipo para un insumo."""
        return self.db.query(Notificacion).filter(
            Notificacion.id_insumo == id_insumo,
            Notificacion.tipo == tipo,
            Notificacion.activa == True
        ).update({"activa": False})
    
    def contar_no_leidas_por_tipo(self) -> dict:
        """Cuenta notificaciones no leídas agrupadas por tipo."""
        result = self.db.query(
            Notificacion.tipo,
            func.count(Notificacion.id_notificacion)
        ).filter(
            Notificacion.activa == True,
            Notificacion.leida == False
        ).group_by(Notificacion.tipo).all()
        
        return {tipo: count for tipo, count in result}
    
    # ==================== CONSULTAS SQL PURAS ====================
    
    def obtener_lotes_por_vencer(self, dias_limite: int = 15) -> List[dict]:
        """
        Obtiene lotes que vencen en los próximos X días.
        Usa SQL puro por tener más de 2 joins implícitos.
        
        Returns:
            Lista de diccionarios con datos del lote, insumo y días restantes.
        """
        sql = text("""
            SELECT 
                d.id_ingreso_detalle,
                d.id_insumo,
                d.cantidad_restante,
                d.fecha_vencimiento,
                d.precio_unitario,
                i.id_ingreso,
                i.numero_ingreso,
                ins.codigo AS codigo_insumo,
                ins.nombre AS nombre_insumo,
                ins.unidad_medida,
                ins.perecible,
                (d.fecha_vencimiento::date - CURRENT_DATE) AS dias_restantes
            FROM ingresos_insumos_detalle d
            INNER JOIN ingresos_insumos i ON d.id_ingreso = i.id_ingreso
            INNER JOIN insumo ins ON d.id_insumo = ins.id_insumo
            WHERE 
                d.cantidad_restante > 0
                AND d.fecha_vencimiento IS NOT NULL
                AND ins.anulado = false
                AND i.anulado = false
                AND (d.fecha_vencimiento::date - CURRENT_DATE) <= :dias_limite
            ORDER BY d.fecha_vencimiento ASC, d.cantidad_restante DESC
        """)
        
        result = self.db.execute(sql, {"dias_limite": dias_limite})
        
        return [dict(row._mapping) for row in result]
    
    def obtener_stock_por_insumo(self) -> List[dict]:
        """
        Obtiene el stock actual de cada insumo (suma de cantidad_restante de todos los lotes).
        Usa SQL puro para agregación con múltiples joins.
        
        Returns:
            Lista de diccionarios con id_insumo, stock_actual, stock_minimo.
        """
        sql = text("""
            SELECT 
                ins.id_insumo,
                ins.codigo,
                ins.nombre,
                ins.unidad_medida,
                ins.stock_minimo,
                COALESCE(SUM(d.cantidad_restante), 0) AS stock_actual
            FROM insumo ins
            LEFT JOIN ingresos_insumos_detalle d ON ins.id_insumo = d.id_insumo
            LEFT JOIN ingresos_insumos i ON d.id_ingreso = i.id_ingreso AND i.anulado = false
            WHERE 
                ins.anulado = false
            GROUP BY 
                ins.id_insumo, 
                ins.codigo, 
                ins.nombre, 
                ins.unidad_medida, 
                ins.stock_minimo
            HAVING 
                COALESCE(SUM(d.cantidad_restante), 0) < ins.stock_minimo
            ORDER BY 
                (COALESCE(SUM(d.cantidad_restante), 0) / NULLIF(ins.stock_minimo, 0)) ASC
        """)
        
        result = self.db.execute(sql)
        
        return [dict(row._mapping) for row in result]
    
    def obtener_lista_usar_hoy(self, dias_rojo: int = 3) -> List[dict]:
        """
        Obtiene lista FEFO de insumos a usar hoy/pronto (vencen en <= dias_rojo días).
        
        Returns:
            Lista ordenada por fecha de vencimiento (más próximo primero).
        """
        sql = text("""
            SELECT 
                d.id_ingreso_detalle,
                d.id_insumo,
                d.cantidad_restante,
                d.fecha_vencimiento,
                d.precio_unitario,
                (d.cantidad_restante * d.precio_unitario) AS valor_estimado,
                ins.codigo AS codigo_insumo,
                ins.nombre AS nombre_insumo,
                ins.unidad_medida,
                (d.fecha_vencimiento::date - CURRENT_DATE) AS dias_restantes,
                ROW_NUMBER() OVER (ORDER BY d.fecha_vencimiento ASC) AS prioridad
            FROM ingresos_insumos_detalle d
            INNER JOIN ingresos_insumos i ON d.id_ingreso = i.id_ingreso
            INNER JOIN insumo ins ON d.id_insumo = ins.id_insumo
            WHERE 
                d.cantidad_restante > 0
                AND d.fecha_vencimiento IS NOT NULL
                AND ins.anulado = false
                AND i.anulado = false
                AND ins.perecible = true
                AND (d.fecha_vencimiento::date - CURRENT_DATE) <= :dias_rojo
            ORDER BY d.fecha_vencimiento ASC
        """)
        
        result = self.db.execute(sql, {"dias_rojo": dias_rojo})
        
        return [dict(row._mapping) for row in result]
    
    def obtener_resumen_semaforo(
        self,
        dias_verde: int = 15,
        dias_amarillo: int = 7,
        dias_rojo: int = 3
    ) -> dict:
        """
        Obtiene conteo de lotes por estado de semáforo.
        
        Returns:
            Diccionario con conteos: verde, amarillo, rojo, vencidos.
        """
        sql = text("""
            SELECT 
                CASE 
                    WHEN (d.fecha_vencimiento::date - CURRENT_DATE) < 0 THEN 'VENCIDO'
                    WHEN (d.fecha_vencimiento::date - CURRENT_DATE) <= :dias_rojo THEN 'ROJO'
                    WHEN (d.fecha_vencimiento::date - CURRENT_DATE) <= :dias_amarillo THEN 'AMARILLO'
                    ELSE 'VERDE'
                END AS semaforo,
                COUNT(*) AS cantidad
            FROM ingresos_insumos_detalle d
            INNER JOIN ingresos_insumos i ON d.id_ingreso = i.id_ingreso
            INNER JOIN insumo ins ON d.id_insumo = ins.id_insumo
            WHERE 
                d.cantidad_restante > 0
                AND d.fecha_vencimiento IS NOT NULL
                AND ins.anulado = false
                AND i.anulado = false
                AND ins.perecible = true
            GROUP BY 
                CASE 
                    WHEN (d.fecha_vencimiento::date - CURRENT_DATE) < 0 THEN 'VENCIDO'
                    WHEN (d.fecha_vencimiento::date - CURRENT_DATE) <= :dias_rojo THEN 'ROJO'
                    WHEN (d.fecha_vencimiento::date - CURRENT_DATE) <= :dias_amarillo THEN 'AMARILLO'
                    ELSE 'VERDE'
                END
        """)
        
        result = self.db.execute(sql, {
            "dias_verde": dias_verde,
            "dias_amarillo": dias_amarillo,
            "dias_rojo": dias_rojo
        })
        
        conteos = {"VERDE": 0, "AMARILLO": 0, "ROJO": 0, "VENCIDO": 0}
        for row in result:
            conteos[row.semaforo] = row.cantidad
        
        return conteos
    
    def verificar_notificacion_existente(
        self,
        id_insumo: int,
        tipo: TipoAlerta,
        id_ingreso_detalle: Optional[int] = None
    ) -> bool:
        """
        Verifica si ya existe una notificación activa para evitar duplicados.
        """
        query = self.db.query(Notificacion).filter(
            Notificacion.id_insumo == id_insumo,
            Notificacion.tipo == tipo,
            Notificacion.activa == True,
            func.date(Notificacion.fecha_creacion) == date.today()
        )
        
        if id_ingreso_detalle:
            query = query.filter(Notificacion.id_ingreso_detalle == id_ingreso_detalle)
        
        return query.first() is not None
