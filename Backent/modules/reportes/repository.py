"""
Repository para el módulo de Reportes.
Consultas SQL para análisis ABC, reporte diario, KPIs y rotación.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_, desc, text
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from .repository_interface import ReportesRepositoryInterface


class ReportesRepository(ReportesRepositoryInterface):
    """Repository con consultas SQL para reportes."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==================== ANÁLISIS ABC ====================
    
    def obtener_ventas_por_producto(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        categoria: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene ventas agrupadas por producto para análisis ABC.
        Ordenado por monto total descendente.
        """
        from modules.gestion_almacen_productos.ventas.model import Venta, VentaDetalle
        from modules.productos_terminados.model import ProductoTerminado
        
        query = self.db.query(
            ProductoTerminado.id_producto,
            ProductoTerminado.codigo_producto.label('codigo'),
            ProductoTerminado.nombre,
            func.sum(VentaDetalle.cantidad).label('cantidad_vendida'),
            func.sum(VentaDetalle.subtotal).label('monto_total'),
            func.count(func.distinct(Venta.id_venta)).label('num_ventas')
        ).join(
            VentaDetalle, ProductoTerminado.id_producto == VentaDetalle.id_producto
        ).join(
            Venta, VentaDetalle.id_venta == Venta.id_venta
        ).filter(
            Venta.anulado == False,
            func.date(Venta.fecha_venta) >= fecha_inicio,
            func.date(Venta.fecha_venta) <= fecha_fin
        ).group_by(
            ProductoTerminado.id_producto,
            ProductoTerminado.codigo_producto,
            ProductoTerminado.nombre
        ).order_by(
            desc('monto_total')
        )
        
        resultados = query.all()
        
        return [
            {
                'id_producto': r.id_producto,
                'codigo': r.codigo,
                'nombre': r.nombre,
                'cantidad_vendida': Decimal(str(r.cantidad_vendida or 0)),
                'monto_total': Decimal(str(r.monto_total or 0)),
                'num_ventas': r.num_ventas or 0
            }
            for r in resultados
        ]
    
    # ==================== REPORTE DIARIO ====================
    
    def obtener_resumen_ventas_dia(self, fecha: date) -> Dict[str, Any]:
        """Obtiene resumen de ventas del día."""
        from modules.gestion_almacen_productos.ventas.model import Venta
        
        resultado = self.db.query(
            func.count(Venta.id_venta).label('cantidad_transacciones'),
            func.coalesce(func.sum(Venta.total), 0).label('total_ventas'),
            func.coalesce(func.sum(
                case((Venta.metodo_pago == 'efectivo', Venta.total), else_=0)
            ), 0).label('total_efectivo'),
            func.coalesce(func.sum(
                case((Venta.metodo_pago == 'tarjeta', Venta.total), else_=0)
            ), 0).label('total_tarjeta'),
            func.coalesce(func.sum(
                case((Venta.metodo_pago == 'transferencia', Venta.total), else_=0)
            ), 0).label('total_transferencia'),
            func.coalesce(func.sum(
                case((Venta.metodo_pago == 'yape', Venta.total), else_=0)
            ), 0).label('total_yape'),
            func.coalesce(func.sum(
                case((Venta.metodo_pago == 'plin', Venta.total), else_=0)
            ), 0).label('total_plin')
        ).filter(
            Venta.anulado == False,
            func.date(Venta.fecha_venta) == fecha
        ).first()
        
        total = Decimal(str(resultado.total_ventas or 0))
        cantidad = resultado.cantidad_transacciones or 0
        
        return {
            'total_ventas': total,
            'cantidad_transacciones': cantidad,
            'ticket_promedio': total / cantidad if cantidad > 0 else Decimal('0'),
            'ventas_por_metodo': {
                'efectivo': Decimal(str(resultado.total_efectivo or 0)),
                'tarjeta': Decimal(str(resultado.total_tarjeta or 0)),
                'transferencia': Decimal(str(resultado.total_transferencia or 0)),
                'yape': Decimal(str(resultado.total_yape or 0)),
                'plin': Decimal(str(resultado.total_plin or 0))
            }
        }
    
    def obtener_resumen_mermas_dia(self, fecha: date) -> Dict[str, Any]:
        """Obtiene resumen de mermas del día."""
        from modules.calidad_desperdicio_merma.model import CalidadDesperdicioMerma
        
        resultado = self.db.query(
            func.count(CalidadDesperdicioMerma.id_merma).label('cantidad_casos'),
            func.coalesce(func.sum(CalidadDesperdicioMerma.cantidad), 0).label('cantidad_total'),
            func.coalesce(func.sum(CalidadDesperdicioMerma.costo_total), 0).label('costo_total')
        ).filter(
            CalidadDesperdicioMerma.anulado == False,
            func.date(CalidadDesperdicioMerma.fecha_caso) == fecha
        ).first()
        
        # Desglose por tipo
        desglose = self.db.query(
            CalidadDesperdicioMerma.tipo,
            func.count(CalidadDesperdicioMerma.id_merma).label('cantidad'),
            func.coalesce(func.sum(CalidadDesperdicioMerma.costo_total), 0).label('costo')
        ).filter(
            CalidadDesperdicioMerma.anulado == False,
            func.date(CalidadDesperdicioMerma.fecha_caso) == fecha
        ).group_by(
            CalidadDesperdicioMerma.tipo
        ).all()
        
        return {
            'cantidad_casos': resultado.cantidad_casos or 0,
            'cantidad_total_kg': Decimal(str(resultado.cantidad_total or 0)),
            'costo_total': Decimal(str(resultado.costo_total or 0)),
            'desglose_por_tipo': {
                d.tipo: {
                    'cantidad': d.cantidad,
                    'costo': Decimal(str(d.costo or 0))
                }
                for d in desglose
            }
        }
    
    def obtener_resumen_produccion_dia(self, fecha: date) -> Dict[str, Any]:
        """Obtiene resumen de producción del día."""
        from modules.gestion_almacen_inusmos.produccion.model import Produccion
        from modules.recetas.model import Receta
        from modules.productos_terminados.model import ProductoTerminado
        
        # Producciones del día
        producciones = self.db.query(
            Produccion.id_produccion,
            Produccion.numero_produccion,
            Receta.nombre_receta,
            ProductoTerminado.nombre.label('producto'),
            Produccion.cantidad_batch,
            Receta.rendimiento_producto_terminado
        ).join(
            Receta, Produccion.id_receta == Receta.id_receta
        ).join(
            ProductoTerminado, Receta.id_producto == ProductoTerminado.id_producto
        ).filter(
            Produccion.anulado == False,
            func.date(Produccion.fecha_produccion) == fecha
        ).all()
        
        total_unidades = sum(
            Decimal(str(p.cantidad_batch)) * Decimal(str(p.rendimiento_producto_terminado))
            for p in producciones
        )
        
        recetas_producidas = [
            {
                'numero_produccion': p.numero_produccion,
                'receta': p.nombre_receta,
                'producto': p.producto,
                'cantidad_batch': Decimal(str(p.cantidad_batch)),
                'unidades_producidas': Decimal(str(p.cantidad_batch)) * Decimal(str(p.rendimiento_producto_terminado))
            }
            for p in producciones
        ]
        
        return {
            'total_producciones': len(producciones),
            'total_unidades_producidas': total_unidades,
            'recetas_producidas': recetas_producidas
        }
    
    # ==================== KPIs ====================
    
    def obtener_kg_totales_dia(self, fecha: date) -> Decimal:
        """
        Obtiene los kg totales manejados en el día.
        Suma de entradas + stock inicial usado.
        """
        from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
        
        # Total de movimientos del día (entradas y salidas)
        resultado = self.db.query(
            func.coalesce(func.sum(MovimientoInsumo.cantidad), 0).label('total')
        ).filter(
            MovimientoInsumo.anulado == False,
            func.date(MovimientoInsumo.fecha_movimiento) == fecha
        ).first()
        
        return Decimal(str(resultado.total or 0))
    
    def contar_lotes_vencidos_hoy(self, fecha: date) -> Dict[str, Any]:
        """Cuenta lotes vencidos a la fecha con stock disponible."""
        from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProductoDetalle
        from modules.insumo.model import Insumo
        
        resultado = self.db.query(
            func.count(IngresoProductoDetalle.id_ingreso_detalle).label('cantidad_lotes'),
            func.coalesce(func.sum(IngresoProductoDetalle.cantidad_restante), 0).label('cantidad_kg')
        ).join(
            Insumo, IngresoProductoDetalle.id_insumo == Insumo.id_insumo
        ).filter(
            IngresoProductoDetalle.cantidad_restante > 0,
            IngresoProductoDetalle.fecha_vencimiento <= fecha,
            Insumo.perecible == True
        ).first()
        
        return {
            'cantidad_lotes': resultado.cantidad_lotes or 0,
            'cantidad_kg': Decimal(str(resultado.cantidad_kg or 0))
        }
    
    def obtener_consumo_insumos_periodo(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> List[Dict[str, Any]]:
        """Obtiene el consumo de insumos en un período."""
        from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
        from modules.insumo.model import Insumo
        
        resultado = self.db.query(
            Insumo.id_insumo,
            Insumo.codigo,
            Insumo.nombre,
            Insumo.unidad_medida,
            func.coalesce(func.sum(
                case((MovimientoInsumo.tipo_movimiento == 'SALIDA', MovimientoInsumo.cantidad), else_=0)
            ), 0).label('consumo_total')
        ).outerjoin(
            MovimientoInsumo, and_(
                Insumo.id_insumo == MovimientoInsumo.id_insumo,
                MovimientoInsumo.anulado == False,
                func.date(MovimientoInsumo.fecha_movimiento) >= fecha_inicio,
                func.date(MovimientoInsumo.fecha_movimiento) <= fecha_fin
            )
        ).filter(
            Insumo.anulado == False
        ).group_by(
            Insumo.id_insumo,
            Insumo.codigo,
            Insumo.nombre,
            Insumo.unidad_medida
        ).all()
        
        return [
            {
                'id_insumo': r.id_insumo,
                'codigo': r.codigo,
                'nombre': r.nombre,
                'unidad_medida': str(r.unidad_medida.value) if r.unidad_medida else '',
                'consumo_total': Decimal(str(r.consumo_total or 0))
            }
            for r in resultado
        ]
    
    def obtener_stock_actual_insumos(self) -> List[Dict[str, Any]]:
        """Obtiene el stock actual de todos los insumos."""
        from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProductoDetalle
        from modules.insumo.model import Insumo
        
        resultado = self.db.query(
            Insumo.id_insumo,
            Insumo.codigo,
            Insumo.nombre,
            Insumo.unidad_medida,
            Insumo.stock_minimo,
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
            Insumo.stock_minimo
        ).all()
        
        return [
            {
                'id_insumo': r.id_insumo,
                'codigo': r.codigo,
                'nombre': r.nombre,
                'unidad_medida': str(r.unidad_medida.value) if r.unidad_medida else '',
                'stock_minimo': Decimal(str(r.stock_minimo or 0)),
                'stock_actual': Decimal(str(r.stock_actual or 0))
            }
            for r in resultado
        ]
    
    # ==================== MÉTODOS FALTANTES PARA INTERFACE ====================
    
    def obtener_tasa_merma_periodo(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Decimal:
        """Calcula la tasa de merma del período."""
        from modules.calidad_desperdicio_merma.model import CalidadDesperdicioMerma
        from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
        
        # Total de mermas del período
        mermas = self.db.query(
            func.coalesce(func.sum(CalidadDesperdicioMerma.cantidad), 0).label('total_merma')
        ).filter(
            CalidadDesperdicioMerma.anulado == False,
            func.date(CalidadDesperdicioMerma.fecha_caso) >= fecha_inicio,
            func.date(CalidadDesperdicioMerma.fecha_caso) <= fecha_fin
        ).first()
        
        # Total de movimientos (entradas) del período
        movimientos = self.db.query(
            func.coalesce(func.sum(MovimientoInsumo.cantidad), 0).label('total_mov')
        ).filter(
            MovimientoInsumo.anulado == False,
            MovimientoInsumo.tipo_movimiento == 'ENTRADA',
            func.date(MovimientoInsumo.fecha_movimiento) >= fecha_inicio,
            func.date(MovimientoInsumo.fecha_movimiento) <= fecha_fin
        ).first()
        
        total_merma = Decimal(str(mermas.total_merma or 0))
        total_mov = Decimal(str(movimientos.total_mov or 1))  # Evitar división por cero
        
        if total_mov == 0:
            return Decimal('0')
        
        return (total_merma / total_mov) * 100
    
    def obtener_rotacion_inventario(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Decimal:
        """Calcula la rotación de inventario del período."""
        from modules.gestion_almacen_productos.ventas.model import Venta, VentaDetalle
        from modules.productos_terminados.model import ProductoTerminado
        
        # Costo de ventas (aproximado como el subtotal de las ventas)
        costo_ventas = self.db.query(
            func.coalesce(func.sum(VentaDetalle.subtotal), 0).label('costo')
        ).join(
            Venta, VentaDetalle.id_venta == Venta.id_venta
        ).filter(
            Venta.anulado == False,
            func.date(Venta.fecha_venta) >= fecha_inicio,
            func.date(Venta.fecha_venta) <= fecha_fin
        ).first()
        
        # Inventario promedio (stock actual * precio)
        inventario = self.db.query(
            func.coalesce(func.sum(ProductoTerminado.stock_actual * ProductoTerminado.precio_venta), 0).label('valor')
        ).filter(
            ProductoTerminado.anulado == False
        ).first()
        
        costo = Decimal(str(costo_ventas.costo or 0))
        valor_inv = Decimal(str(inventario.valor or 1))  # Evitar división por cero
        
        if valor_inv == 0:
            return Decimal('0')
        
        # Rotación anualizada
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        factor_anualizacion = Decimal('365') / Decimal(str(dias_periodo))
        
        return (costo / valor_inv) * factor_anualizacion
    
    def obtener_valor_inventario_actual(self) -> Decimal:
        """Obtiene el valor total del inventario actual."""
        from modules.productos_terminados.model import ProductoTerminado
        from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProductoDetalle
        
        # Valor de productos terminados
        valor_productos = self.db.query(
            func.coalesce(func.sum(ProductoTerminado.stock_actual * ProductoTerminado.precio_venta), 0).label('valor')
        ).filter(
            ProductoTerminado.anulado == False
        ).first()
        
        # Valor de insumos (stock restante * precio unitario del lote)
        valor_insumos = self.db.query(
            func.coalesce(func.sum(IngresoProductoDetalle.cantidad_restante * IngresoProductoDetalle.precio_unitario), 0).label('valor')
        ).filter(
            IngresoProductoDetalle.cantidad_restante > 0
        ).first()
        
        total_productos = Decimal(str(valor_productos.valor or 0))
        total_insumos = Decimal(str(valor_insumos.valor or 0))
        
        return total_productos + total_insumos
    
    def obtener_rotacion_por_producto(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        limite: int = 50
    ) -> List[Dict[str, Any]]:
        """Obtiene la rotación de cada producto en el período."""
        from modules.gestion_almacen_productos.ventas.model import Venta, VentaDetalle
        from modules.productos_terminados.model import ProductoTerminado
        
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        
        # Subquery para ventas del período
        subquery = self.db.query(
            VentaDetalle.id_producto,
            func.sum(VentaDetalle.cantidad).label('vendido'),
            func.sum(VentaDetalle.subtotal).label('valor_vendido')
        ).join(
            Venta, VentaDetalle.id_venta == Venta.id_venta
        ).filter(
            Venta.anulado == False,
            func.date(Venta.fecha_venta) >= fecha_inicio,
            func.date(Venta.fecha_venta) <= fecha_fin
        ).group_by(
            VentaDetalle.id_producto
        ).subquery()
        
        # Query principal
        resultado = self.db.query(
            ProductoTerminado.id_producto,
            ProductoTerminado.codigo_producto.label('codigo'),
            ProductoTerminado.nombre,
            ProductoTerminado.stock_actual,
            ProductoTerminado.precio_venta,
            func.coalesce(subquery.c.vendido, 0).label('cantidad_vendida'),
            func.coalesce(subquery.c.valor_vendido, 0).label('valor_vendido')
        ).outerjoin(
            subquery, ProductoTerminado.id_producto == subquery.c.id_producto
        ).filter(
            ProductoTerminado.anulado == False
        ).order_by(
            desc('cantidad_vendida')
        ).limit(limite).all()
        
        items = []
        for r in resultado:
            stock = Decimal(str(r.stock_actual or 0))
            vendido = Decimal(str(r.cantidad_vendida or 0))
            valor_inventario = stock * Decimal(str(r.precio_venta or 0))
            
            # Calcular rotación
            if valor_inventario > 0 and vendido > 0:
                rotacion = (Decimal(str(r.valor_vendido or 0)) / valor_inventario) * (Decimal('365') / Decimal(str(dias_periodo)))
            else:
                rotacion = Decimal('0')
            
            items.append({
                'id_producto': r.id_producto,
                'codigo': r.codigo,
                'nombre': r.nombre,
                'stock_actual': stock,
                'cantidad_vendida': vendido,
                'valor_vendido': Decimal(str(r.valor_vendido or 0)),
                'valor_inventario': valor_inventario,
                'rotacion_anualizada': round(rotacion, 2),
                'dias_inventario': round(Decimal(str(dias_periodo)) * stock / vendido, 0) if vendido > 0 else None
            })
        
        return items
    
    def obtener_productos_sin_movimiento(
        self,
        dias: int = 30
    ) -> List[Dict[str, Any]]:
        """Obtiene productos sin movimiento en los últimos X días."""
        from modules.gestion_almacen_productos.ventas.model import Venta, VentaDetalle
        from modules.productos_terminados.model import ProductoTerminado
        
        fecha_limite = date.today() - timedelta(days=dias)
        
        # Subquery para productos con ventas recientes
        productos_con_venta = self.db.query(
            VentaDetalle.id_producto
        ).join(
            Venta, VentaDetalle.id_venta == Venta.id_venta
        ).filter(
            Venta.anulado == False,
            func.date(Venta.fecha_venta) >= fecha_limite
        ).distinct().subquery()
        
        # Productos sin ventas recientes
        resultado = self.db.query(
            ProductoTerminado.id_producto,
            ProductoTerminado.codigo_producto.label('codigo'),
            ProductoTerminado.nombre,
            ProductoTerminado.stock_actual,
            ProductoTerminado.precio_venta
        ).outerjoin(
            productos_con_venta, ProductoTerminado.id_producto == productos_con_venta.c.id_producto
        ).filter(
            ProductoTerminado.anulado == False,
            ProductoTerminado.stock_actual > 0,
            productos_con_venta.c.id_producto == None  # Sin ventas recientes
        ).all()
        
        return [
            {
                'id_producto': r.id_producto,
                'codigo': r.codigo,
                'nombre': r.nombre,
                'stock_actual': Decimal(str(r.stock_actual or 0)),
                'valor_inventario': Decimal(str(r.stock_actual or 0)) * Decimal(str(r.precio_venta or 0)),
                'dias_sin_movimiento': dias,
                'alerta': 'REVISAR' if Decimal(str(r.stock_actual or 0)) > 0 else 'OK'
            }
            for r in resultado
        ]
    
    # ==================== ROTACIÓN ====================
    
    def obtener_rotacion_productos_terminados(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Obtiene datos de rotación para productos terminados."""
        from modules.gestion_almacen_productos.ventas.model import Venta, VentaDetalle
        from modules.productos_terminados.model import ProductoTerminado
        
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        
        # Subquery para ventas del período
        subquery = self.db.query(
            VentaDetalle.id_producto,
            func.sum(VentaDetalle.cantidad).label('vendido')
        ).join(
            Venta, VentaDetalle.id_venta == Venta.id_venta
        ).filter(
            Venta.anulado == False,
            func.date(Venta.fecha_venta) >= fecha_inicio,
            func.date(Venta.fecha_venta) <= fecha_fin
        ).group_by(
            VentaDetalle.id_producto
        ).subquery()
        
        # Query principal
        query = self.db.query(
            ProductoTerminado.id_producto,
            ProductoTerminado.codigo_producto.label('codigo'),
            ProductoTerminado.nombre,
            ProductoTerminado.unidad_medida,
            ProductoTerminado.stock_actual,
            func.coalesce(subquery.c.vendido, 0).label('consumo_periodo')
        ).outerjoin(
            subquery, ProductoTerminado.id_producto == subquery.c.id_producto
        ).filter(
            ProductoTerminado.anulado == False
        )
        
        total = query.count()
        resultados = query.offset(offset).limit(limit).all()
        
        return {
            'items': [
                {
                    'id': r.id_producto,
                    'codigo': r.codigo,
                    'nombre': r.nombre,
                    'tipo': 'producto_terminado',
                    'unidad_medida': str(r.unidad_medida.value) if r.unidad_medida else '',
                    'stock_actual': Decimal(str(r.stock_actual or 0)),
                    'consumo_periodo': Decimal(str(r.consumo_periodo or 0)),
                    'dias_periodo': dias_periodo
                }
                for r in resultados
            ],
            'total': total
        }
    
    def obtener_rotacion_insumos(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Obtiene datos de rotación para insumos."""
        from modules.gestion_almacen_inusmos.movimiento_insumos.model import MovimientoInsumo
        from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProductoDetalle
        from modules.insumo.model import Insumo
        
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        
        # Subquery para consumo (salidas) del período
        subquery_consumo = self.db.query(
            MovimientoInsumo.id_insumo,
            func.sum(MovimientoInsumo.cantidad).label('consumido')
        ).filter(
            MovimientoInsumo.anulado == False,
            MovimientoInsumo.tipo_movimiento == 'SALIDA',
            func.date(MovimientoInsumo.fecha_movimiento) >= fecha_inicio,
            func.date(MovimientoInsumo.fecha_movimiento) <= fecha_fin
        ).group_by(
            MovimientoInsumo.id_insumo
        ).subquery()
        
        # Subquery para stock actual
        subquery_stock = self.db.query(
            IngresoProductoDetalle.id_insumo,
            func.sum(IngresoProductoDetalle.cantidad_restante).label('stock')
        ).group_by(
            IngresoProductoDetalle.id_insumo
        ).subquery()
        
        # Query principal
        query = self.db.query(
            Insumo.id_insumo,
            Insumo.codigo,
            Insumo.nombre,
            Insumo.unidad_medida,
            func.coalesce(subquery_stock.c.stock, 0).label('stock_actual'),
            func.coalesce(subquery_consumo.c.consumido, 0).label('consumo_periodo')
        ).outerjoin(
            subquery_stock, Insumo.id_insumo == subquery_stock.c.id_insumo
        ).outerjoin(
            subquery_consumo, Insumo.id_insumo == subquery_consumo.c.id_insumo
        ).filter(
            Insumo.anulado == False
        )
        
        total = query.count()
        resultados = query.offset(offset).limit(limit).all()
        
        return {
            'items': [
                {
                    'id': r.id_insumo,
                    'codigo': r.codigo,
                    'nombre': r.nombre,
                    'tipo': 'insumo',
                    'unidad_medida': str(r.unidad_medida.value) if r.unidad_medida else '',
                    'stock_actual': Decimal(str(r.stock_actual or 0)),
                    'consumo_periodo': Decimal(str(r.consumo_periodo or 0)),
                    'dias_periodo': dias_periodo
                }
                for r in resultados
            ],
            'total': total
        }
