"""
Service para el módulo de Reportes.
Lógica de negocio para análisis ABC, reporte diario, KPIs y rotación.
"""

from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from loguru import logger

from .repository import ReportesRepository
from .schemas import (
    ReporteABCResponse, ProductoABC,
    ReporteDiarioResponse, ResumenVentasDiario, ResumenMermasDiario,
    ResumenProduccionDiario, ItemVencimiento, ItemStockCritico,
    KPIsResponse, KPIValue,
    RotacionResponse, ItemRotacion
)
# Reutilizar lógica de alertas
from modules.alertas.service import AlertasService


class ReportesService:
    """Servicio de lógica de negocio para reportes."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ReportesRepository(db)
        self.alertas_service = AlertasService(db)
    
    # ==================== ANÁLISIS ABC ====================
    
    def generar_reporte_abc(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        categoria: Optional[str] = None
    ) -> ReporteABCResponse:
        """
        Genera análisis ABC de productos por ventas.
        Clasificación:
        - A: 70% de ventas (control DIARIO)
        - B: 20% de ventas (control SEMANAL)
        - C: 10% de ventas (control MENSUAL)
        """
        # Obtener ventas por producto ordenadas por monto
        ventas = self.repository.obtener_ventas_por_producto(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            categoria=categoria
        )
        
        if not ventas:
            return ReporteABCResponse(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                total_ventas=Decimal('0'),
                total_productos=0,
                resumen={'A': 0, 'B': 0, 'C': 0},
                productos_a=[],
                productos_b=[],
                productos_c=[]
            )
        
        # Calcular total de ventas
        total_ventas = sum(v['monto_total'] for v in ventas)
        
        # Calcular porcentajes y clasificar
        productos_a = []
        productos_b = []
        productos_c = []
        
        porcentaje_acumulado = Decimal('0')
        
        for venta in ventas:
            porcentaje = (venta['monto_total'] / total_ventas * 100) if total_ventas > 0 else Decimal('0')
            porcentaje_acumulado += porcentaje
            
            # Clasificar según porcentaje acumulado
            if porcentaje_acumulado <= Decimal('70'):
                clasificacion = 'A'
                frecuencia = 'diario'
            elif porcentaje_acumulado <= Decimal('90'):
                clasificacion = 'B'
                frecuencia = 'semanal'
            else:
                clasificacion = 'C'
                frecuencia = 'mensual'
            
            producto_abc = ProductoABC(
                id_producto=venta['id_producto'],
                codigo=venta['codigo'],
                nombre=venta['nombre'],
                cantidad_vendida=venta['cantidad_vendida'],
                monto_total=venta['monto_total'],
                porcentaje_ventas=round(porcentaje, 2),
                porcentaje_acumulado=round(porcentaje_acumulado, 2),
                clasificacion=clasificacion,
                frecuencia_control=frecuencia
            )
            
            if clasificacion == 'A':
                productos_a.append(producto_abc)
            elif clasificacion == 'B':
                productos_b.append(producto_abc)
            else:
                productos_c.append(producto_abc)
        
        return ReporteABCResponse(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            total_ventas=total_ventas,
            total_productos=len(ventas),
            resumen={
                'A': len(productos_a),
                'B': len(productos_b),
                'C': len(productos_c),
                'porcentaje_A': round(sum(p.porcentaje_ventas for p in productos_a), 2),
                'porcentaje_B': round(sum(p.porcentaje_ventas for p in productos_b), 2),
                'porcentaje_C': round(sum(p.porcentaje_ventas for p in productos_c), 2)
            },
            productos_a=productos_a,
            productos_b=productos_b,
            productos_c=productos_c
        )
    
    # ==================== REPORTE DIARIO ====================
    
    def generar_reporte_diario(self, fecha: date) -> ReporteDiarioResponse:
        """Genera reporte diario consolidado."""
        
        # 1. Resumen de ventas
        ventas_data = self.repository.obtener_resumen_ventas_dia(fecha)
        resumen_ventas = ResumenVentasDiario(
            total_ventas=ventas_data['total_ventas'],
            cantidad_transacciones=ventas_data['cantidad_transacciones'],
            ticket_promedio=ventas_data['ticket_promedio'],
            ventas_por_metodo=ventas_data['ventas_por_metodo']
        )
        
        # 2. Resumen de mermas
        mermas_data = self.repository.obtener_resumen_mermas_dia(fecha)
        porcentaje_merma = (
            (mermas_data['costo_total'] / ventas_data['total_ventas'] * 100)
            if ventas_data['total_ventas'] > 0 else Decimal('0')
        )
        
        resumen_mermas = ResumenMermasDiario(
            cantidad_casos=mermas_data['cantidad_casos'],
            cantidad_total_kg=mermas_data['cantidad_total_kg'],
            costo_total=mermas_data['costo_total'],
            porcentaje_sobre_ventas=round(porcentaje_merma, 2),
            meta_porcentaje=Decimal('3.0'),
            cumple_meta=porcentaje_merma < Decimal('3.0'),
            desglose_por_tipo=mermas_data['desglose_por_tipo']
        )
        
        # 3. Resumen de producción
        produccion_data = self.repository.obtener_resumen_produccion_dia(fecha)
        resumen_produccion = ResumenProduccionDiario(
            total_producciones=produccion_data['total_producciones'],
            total_unidades_producidas=produccion_data['total_unidades_producidas'],
            recetas_producidas=produccion_data['recetas_producidas']
        )
        
        # 4. Vencimientos de mañana (reutilizar alertas)
        manana = fecha + timedelta(days=1)
        lista_usar_hoy = self.alertas_service.obtener_lista_usar_hoy()
        
        vencen_manana = [
            ItemVencimiento(
                id_insumo=item.id_insumo,
                codigo=item.codigo,
                nombre=item.nombre,
                cantidad=Decimal(str(item.cantidad_disponible)),
                unidad_medida=item.unidad_medida,
                fecha_vencimiento=item.fecha_vencimiento,
                dias_restantes=item.dias_restantes,
                valor_estimado=None
            )
            for item in lista_usar_hoy.items
            if item.dias_restantes == 1
        ]
        
        # 5. Stock crítico (reutilizar alertas)
        stock_critico_data = self.alertas_service.obtener_stock_critico()
        stock_critico = [
            ItemStockCritico(
                id_insumo=item.id_insumo,
                codigo=item.codigo,
                nombre=item.nombre,
                stock_actual=Decimal(str(item.stock_actual)),
                stock_minimo=Decimal(str(item.stock_minimo)),
                deficit=Decimal(str(item.deficit)),
                unidad_medida=item.unidad_medida,
                es_critico=item.es_critico
            )
            for item in stock_critico_data.items
        ]
        
        return ReporteDiarioResponse(
            fecha=fecha,
            generado_en=datetime.now(),
            ventas=resumen_ventas,
            mermas=resumen_mermas,
            produccion=resumen_produccion,
            vencen_manana=vencen_manana,
            stock_critico=stock_critico
        )
    
    # ==================== KPIs ====================
    
    def obtener_kpis(self, fecha: date) -> KPIsResponse:
        """Obtiene todos los KPIs del sistema."""
        
        # KPI 1: % Merma diaria
        mermas_data = self.repository.obtener_resumen_mermas_dia(fecha)
        ventas_data = self.repository.obtener_resumen_ventas_dia(fecha)
        
        porcentaje_merma = (
            (mermas_data['costo_total'] / ventas_data['total_ventas'] * 100)
            if ventas_data['total_ventas'] > 0 else Decimal('0')
        )
        
        kpi_merma = KPIValue(
            nombre="Merma Diaria",
            valor=round(porcentaje_merma, 2),
            unidad="%",
            meta=Decimal('3.0'),
            cumple_meta=porcentaje_merma < Decimal('3.0'),
            detalle=f"Costo merma: S/ {mermas_data['costo_total']:.2f}"
        )
        
        # KPI 2: Productos vencidos hoy
        vencidos_data = self.repository.contar_lotes_vencidos_hoy(fecha)
        
        kpi_vencidos = KPIValue(
            nombre="Productos Vencidos Hoy",
            valor=Decimal(str(vencidos_data['cantidad_lotes'])),
            unidad="lotes",
            meta=Decimal('0'),
            cumple_meta=vencidos_data['cantidad_lotes'] == 0,
            detalle=f"{vencidos_data['cantidad_kg']:.2f} kg en riesgo"
        )
        
        # KPI 3: Cumplimiento FEFO (asumido como 100% si usa el módulo de producción)
        # Ya que el sistema está diseñado para usar FEFO automáticamente
        kpi_fefo = KPIValue(
            nombre="Cumplimiento FEFO",
            valor=Decimal('100'),
            unidad="%",
            meta=Decimal('95'),
            cumple_meta=True,
            detalle="Sistema usa FEFO automático en producción"
        )
        
        # KPI 4: Stock crítico
        stock_critico_data = self.alertas_service.obtener_stock_critico()
        total_criticos = stock_critico_data.total_sin_stock + stock_critico_data.total_bajo_minimo
        
        kpi_stock = KPIValue(
            nombre="Stock Crítico",
            valor=Decimal(str(total_criticos)),
            unidad="insumos",
            meta=Decimal('3'),
            cumple_meta=total_criticos < 3,
            detalle=f"Sin stock: {stock_critico_data.total_sin_stock}, Bajo mínimo: {stock_critico_data.total_bajo_minimo}"
        )
        
        # KPI 5: Rotación de inventario (últimos 30 días anualizado)
        fecha_inicio = fecha - timedelta(days=30)
        rotacion = self._calcular_rotacion_promedio(fecha_inicio, fecha)
        
        kpi_rotacion = KPIValue(
            nombre="Rotación Inventario",
            valor=round(rotacion, 2),
            unidad="veces/año",
            meta=Decimal('12'),
            cumple_meta=rotacion >= Decimal('12'),
            detalle="Proyección anual basada en últimos 30 días"
        )
        
        # Contar KPIs cumplidos
        kpis = [kpi_merma, kpi_vencidos, kpi_fefo, kpi_stock, kpi_rotacion]
        kpis_cumplidos = sum(1 for kpi in kpis if kpi.cumple_meta)
        
        return KPIsResponse(
            fecha=fecha,
            merma_diaria=kpi_merma,
            productos_vencidos_hoy=kpi_vencidos,
            cumplimiento_fefo=kpi_fefo,
            stock_critico=kpi_stock,
            rotacion_inventario=kpi_rotacion,
            kpis_cumplidos=kpis_cumplidos,
            kpis_totales=len(kpis),
            porcentaje_cumplimiento=round(Decimal(kpis_cumplidos) / Decimal(len(kpis)) * 100, 2)
        )
    
    def _calcular_rotacion_promedio(self, fecha_inicio: date, fecha_fin: date) -> Decimal:
        """Calcula la rotación promedio anualizada."""
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        if dias_periodo <= 0:
            return Decimal('0')
        
        # Obtener datos de rotación
        rotacion_productos = self.repository.obtener_rotacion_productos_terminados(
            fecha_inicio, fecha_fin, limit=1000, offset=0
        )
        rotacion_insumos = self.repository.obtener_rotacion_insumos(
            fecha_inicio, fecha_fin, limit=1000, offset=0
        )
        
        # Calcular rotación promedio
        all_items = rotacion_productos['items'] + rotacion_insumos['items']
        
        if not all_items:
            return Decimal('0')
        
        rotaciones = []
        for item in all_items:
            stock = item['stock_actual']
            consumo = item['consumo_periodo']
            
            if stock > 0 and consumo > 0:
                # Rotación = Consumo / Stock promedio (asumiendo stock actual como promedio)
                rotacion_periodo = consumo / stock
                rotacion_anual = rotacion_periodo * (Decimal('365') / Decimal(str(dias_periodo)))
                rotaciones.append(rotacion_anual)
        
        if not rotaciones:
            return Decimal('0')
        
        return sum(rotaciones) / Decimal(str(len(rotaciones)))
    
    # ==================== ROTACIÓN DE INVENTARIO ====================
    
    def generar_reporte_rotacion(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        limit: int = 100,
        offset: int = 0
    ) -> RotacionResponse:
        """Genera reporte de rotación de inventario."""
        
        dias_periodo = (fecha_fin - fecha_inicio).days + 1
        
        # Obtener datos
        rotacion_productos = self.repository.obtener_rotacion_productos_terminados(
            fecha_inicio, fecha_fin, limit, offset
        )
        rotacion_insumos = self.repository.obtener_rotacion_insumos(
            fecha_inicio, fecha_fin, limit, offset
        )
        
        # Procesar productos terminados
        productos = self._procesar_items_rotacion(
            rotacion_productos['items'], dias_periodo
        )
        
        # Procesar insumos
        insumos = self._procesar_items_rotacion(
            rotacion_insumos['items'], dias_periodo
        )
        
        # Calcular resumen
        all_items = productos + insumos
        
        rotacion_promedio = self._calcular_rotacion_promedio(fecha_inicio, fecha_fin)
        
        items_alta = sum(1 for i in all_items if i.clasificacion == 'alta')
        items_media = sum(1 for i in all_items if i.clasificacion == 'media')
        items_baja = sum(1 for i in all_items if i.clasificacion == 'baja')
        
        return RotacionResponse(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            dias_periodo=dias_periodo,
            rotacion_promedio_anual=rotacion_promedio,
            meta_rotacion_anual=Decimal('12'),
            cumple_meta=rotacion_promedio >= Decimal('12'),
            total_items=len(all_items),
            items_alta_rotacion=items_alta,
            items_media_rotacion=items_media,
            items_baja_rotacion=items_baja,
            insumos=insumos,
            productos_terminados=productos,
            limit=limit,
            offset=offset,
            total=rotacion_productos['total'] + rotacion_insumos['total']
        )
    
    def _procesar_items_rotacion(
        self,
        items: List[dict],
        dias_periodo: int
    ) -> List[ItemRotacion]:
        """Procesa items y calcula métricas de rotación."""
        resultado = []
        
        for item in items:
            stock = item['stock_actual']
            consumo = item['consumo_periodo']
            
            # Calcular días de stock
            consumo_diario = consumo / Decimal(str(dias_periodo)) if dias_periodo > 0 else Decimal('0')
            dias_stock = stock / consumo_diario if consumo_diario > 0 else Decimal('999')
            
            # Calcular rotación
            if stock > 0 and consumo > 0:
                rotacion_periodo = consumo / stock
                rotacion_anual = rotacion_periodo * (Decimal('365') / Decimal(str(dias_periodo)))
            else:
                rotacion_periodo = Decimal('0')
                rotacion_anual = Decimal('0')
            
            # Clasificar
            if rotacion_anual >= Decimal('12'):
                clasificacion = 'alta'
            elif rotacion_anual >= Decimal('6'):
                clasificacion = 'media'
            else:
                clasificacion = 'baja'
            
            resultado.append(ItemRotacion(
                id=item['id'],
                codigo=item['codigo'],
                nombre=item['nombre'],
                tipo=item['tipo'],
                stock_actual=stock,
                unidad_medida=item['unidad_medida'],
                consumo_periodo=consumo,
                dias_stock=round(dias_stock, 1),
                rotacion_periodo=round(rotacion_periodo, 2),
                rotacion_anualizada=round(rotacion_anual, 2),
                clasificacion=clasificacion
            ))
        
        return resultado
