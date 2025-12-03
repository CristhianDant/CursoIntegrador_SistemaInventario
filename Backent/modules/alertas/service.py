from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from loguru import logger

from .model import Notificacion, TipoAlerta, SemaforoEstado
from .repository import AlertasRepository
from .schemas import (
    NotificacionResponse,
    ResumenSemaforo,
    InsumoSemaforo,
    ResumenStockCritico,
    InsumoStockCritico,
    ListaUsarHoy,
    ItemUsarHoy,
    ResumenAlertas,
    SemaforoEstadoEnum
)
from modules.empresa.model import Empresa, DEFAULT_CONFIGURACION_ALERTAS
from .service_interface import AlertasServiceInterface


class AlertasService(AlertasServiceInterface):
    """Servicio para la lógica de negocio del módulo de alertas."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = AlertasRepository(db)
    
    # ==================== CONFIGURACIÓN ====================
    
    def obtener_configuracion_alertas(self, id_empresa: int = 1) -> dict:
        """Obtiene la configuración de alertas de la empresa."""
        empresa = self.db.query(Empresa).filter(
            Empresa.id_empresa == id_empresa
        ).first()
        
        if empresa:
            return empresa.get_configuracion_alertas()
        
        return DEFAULT_CONFIGURACION_ALERTAS.copy()
    
    def actualizar_configuracion_alertas(
        self,
        id_empresa: int,
        configuracion: dict
    ) -> dict:
        """Actualiza la configuración de alertas de la empresa."""
        empresa = self.db.query(Empresa).filter(
            Empresa.id_empresa == id_empresa
        ).first()
        
        if not empresa:
            raise ValueError(f"Empresa con ID {id_empresa} no encontrada")
        
        # Merge con configuración existente
        config_actual = empresa.get_configuracion_alertas()
        config_actual.update(configuracion)
        
        empresa.configuracion_alertas = config_actual
        self.db.commit()
        
        logger.info(f"Configuración de alertas actualizada para empresa {id_empresa}")
        return config_actual
    
    # ==================== NOTIFICACIONES ====================
    
    def obtener_notificaciones(
        self,
        tipo: Optional[str] = None,
        solo_no_leidas: bool = False,
        limit: int = 100
    ) -> List[NotificacionResponse]:
        """Obtiene lista de notificaciones con filtros."""
        tipo_enum = TipoAlerta(tipo) if tipo else None
        
        notificaciones = self.repository.obtener_notificaciones_activas(
            tipo=tipo_enum,
            solo_no_leidas=solo_no_leidas,
            limit=limit
        )
        
        # Mapear a response con datos del insumo
        result = []
        for n in notificaciones:
            response = NotificacionResponse(
                id_notificacion=n.id_notificacion,
                tipo=n.tipo,
                titulo=n.titulo,
                mensaje=n.mensaje,
                id_insumo=n.id_insumo,
                id_ingreso_detalle=n.id_ingreso_detalle,
                semaforo=n.semaforo,
                dias_restantes=n.dias_restantes,
                cantidad_afectada=n.cantidad_afectada,
                leida=n.leida,
                activa=n.activa,
                fecha_creacion=n.fecha_creacion,
                fecha_lectura=n.fecha_lectura,
                nombre_insumo=getattr(n, 'nombre_insumo', None),
                codigo_insumo=getattr(n, 'codigo_insumo', None)
            )
            result.append(response)
        
        return result
    
    def marcar_notificacion_leida(self, id_notificacion: int) -> bool:
        """Marca una notificación como leída."""
        result = self.repository.marcar_como_leida(id_notificacion)
        self.db.commit()
        return result
    
    def marcar_todas_leidas(self, tipo: Optional[str] = None) -> int:
        """Marca todas las notificaciones como leídas."""
        tipo_enum = TipoAlerta(tipo) if tipo else None
        count = self.repository.marcar_todas_como_leidas(tipo=tipo_enum)
        self.db.commit()
        return count
    
    def obtener_resumen_alertas(self) -> ResumenAlertas:
        """Obtiene resumen de alertas activas."""
        conteos = self.repository.contar_no_leidas_por_tipo()
        total = sum(conteos.values())
        
        return ResumenAlertas(
            fecha=date.today(),
            total_no_leidas=total,
            por_tipo=conteos,
            ultima_ejecucion_job=None  # TODO: Guardar en algún lado
        )
    
    # ==================== SEMÁFORO DE VENCIMIENTOS ====================
    
    def obtener_semaforo_vencimientos(self, id_empresa: int = 1) -> ResumenSemaforo:
        """Obtiene el semáforo completo de vencimientos."""
        config = self.obtener_configuracion_alertas(id_empresa)
        dias_verde = config["dias_verde"]
        dias_amarillo = config["dias_amarillo"]
        dias_rojo = config["dias_rojo"]
        
        # Obtener conteos
        conteos = self.repository.obtener_resumen_semaforo(
            dias_verde=dias_verde,
            dias_amarillo=dias_amarillo,
            dias_rojo=dias_rojo
        )
        
        # Obtener items rojos y amarillos
        lotes = self.repository.obtener_lotes_por_vencer(dias_limite=dias_amarillo)
        
        items_rojo = []
        items_amarillo = []
        
        for lote in lotes:
            dias_restantes = lote["dias_restantes"]
            
            if dias_restantes < 0:
                semaforo = SemaforoEstadoEnum.ROJO
                accion = "¡VENCIDO! Retirar del inventario"
            elif dias_restantes <= dias_rojo:
                semaforo = SemaforoEstadoEnum.ROJO
                accion = "Usar hoy - Prioridad máxima"
            else:
                semaforo = SemaforoEstadoEnum.AMARILLO
                accion = "Usar esta semana"
            
            item = InsumoSemaforo(
                id_insumo=lote["id_insumo"],
                codigo=lote["codigo_insumo"],
                nombre=lote["nombre_insumo"],
                unidad_medida=str(lote["unidad_medida"]),
                cantidad_disponible=float(lote["cantidad_restante"]),
                fecha_vencimiento=lote["fecha_vencimiento"].date() if hasattr(lote["fecha_vencimiento"], 'date') else lote["fecha_vencimiento"],
                dias_restantes=dias_restantes,
                semaforo=semaforo,
                accion_sugerida=accion,
                id_ingreso_detalle=lote["id_ingreso_detalle"],
                numero_lote=lote["numero_ingreso"]
            )
            
            if dias_restantes <= dias_rojo:
                items_rojo.append(item)
            else:
                items_amarillo.append(item)
        
        return ResumenSemaforo(
            fecha_consulta=date.today(),
            total_verde=conteos.get("VERDE", 0),
            total_amarillo=conteos.get("AMARILLO", 0),
            total_rojo=conteos.get("ROJO", 0),
            total_vencidos=conteos.get("VENCIDO", 0),
            items_rojo=items_rojo,
            items_amarillo=items_amarillo
        )
    
    def obtener_items_rojos(self, id_empresa: int = 1) -> List[InsumoSemaforo]:
        """Obtiene solo los items en estado rojo."""
        semaforo = self.obtener_semaforo_vencimientos(id_empresa)
        return semaforo.items_rojo
    
    def obtener_items_amarillos(self, id_empresa: int = 1) -> List[InsumoSemaforo]:
        """Obtiene solo los items en estado amarillo."""
        semaforo = self.obtener_semaforo_vencimientos(id_empresa)
        return semaforo.items_amarillo
    
    # ==================== STOCK CRÍTICO ====================
    
    def obtener_stock_critico(self) -> ResumenStockCritico:
        """Obtiene resumen de insumos con stock crítico."""
        insumos_bajo_minimo = self.repository.obtener_stock_por_insumo()
        
        items = []
        total_sin_stock = 0
        total_bajo_minimo = 0
        
        for insumo in insumos_bajo_minimo:
            stock_actual = float(insumo["stock_actual"])
            stock_minimo = float(insumo["stock_minimo"])
            
            es_critico = stock_actual == 0
            if es_critico:
                total_sin_stock += 1
            else:
                total_bajo_minimo += 1
            
            porcentaje = (stock_actual / stock_minimo * 100) if stock_minimo > 0 else 0
            
            item = InsumoStockCritico(
                id_insumo=insumo["id_insumo"],
                codigo=insumo["codigo"],
                nombre=insumo["nombre"],
                unidad_medida=str(insumo["unidad_medida"]),
                stock_actual=stock_actual,
                stock_minimo=stock_minimo,
                deficit=stock_minimo - stock_actual,
                es_critico=es_critico,
                porcentaje_stock=round(porcentaje, 2)
            )
            items.append(item)
        
        return ResumenStockCritico(
            fecha_consulta=date.today(),
            total_sin_stock=total_sin_stock,
            total_bajo_minimo=total_bajo_minimo,
            total_normal=0,  # No se incluyen en la query
            items=items
        )
    
    # ==================== USAR HOY (FEFO) ====================
    
    def obtener_lista_usar_hoy(self, id_empresa: int = 1) -> ListaUsarHoy:
        """Obtiene lista FEFO de items a usar hoy."""
        config = self.obtener_configuracion_alertas(id_empresa)
        dias_rojo = config["dias_rojo"]
        
        lotes = self.repository.obtener_lista_usar_hoy(dias_rojo=dias_rojo)
        
        items = []
        valor_total = 0.0
        
        for lote in lotes:
            valor_estimado = float(lote.get("valor_estimado", 0) or 0)
            valor_total += valor_estimado
            
            item = ItemUsarHoy(
                id_insumo=lote["id_insumo"],
                codigo=lote["codigo_insumo"],
                nombre=lote["nombre_insumo"],
                unidad_medida=str(lote["unidad_medida"]),
                cantidad_disponible=float(lote["cantidad_restante"]),
                fecha_vencimiento=lote["fecha_vencimiento"].date() if hasattr(lote["fecha_vencimiento"], 'date') else lote["fecha_vencimiento"],
                dias_restantes=lote["dias_restantes"],
                prioridad=lote["prioridad"],
                id_ingreso_detalle=lote["id_ingreso_detalle"],
                numero_lote=None
            )
            items.append(item)
        
        return ListaUsarHoy(
            fecha=date.today(),
            total_items=len(items),
            valor_estimado_en_riesgo=round(valor_total, 2),
            items=items
        )
