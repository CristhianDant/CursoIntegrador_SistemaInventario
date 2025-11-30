from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from .repository import PromocionRepository
from .model import Promocion, EstadoPromocion, TipoPromocion
from .schemas import (
    PromocionCreate, PromocionUpdate, PromocionResponse, 
    SugerenciaPromocion, EstadisticasPromociones, ProductoComboResponse
)
from modules.productos_terminados.model import ProductoTerminado
from modules.gestion_almacen_productos.movimiento_productos_terminados.model import MovimientoProductoTerminado

class PromocionService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = PromocionRepository(db)

    def _to_response(self, promocion: Promocion) -> PromocionResponse:
        """Convierte un modelo a response con información adicional"""
        productos_combo = None
        if promocion.productos_combo:
            productos_combo = [
                ProductoComboResponse(
                    id=pc.id,
                    id_producto=pc.id_producto,
                    cantidad=pc.cantidad,
                    descuento_individual=float(pc.descuento_individual or 0),
                    nombre_producto=pc.producto.nombre if pc.producto else None
                )
                for pc in promocion.productos_combo
            ]

        return PromocionResponse(
            id_promocion=promocion.id_promocion,
            codigo_promocion=promocion.codigo_promocion,
            titulo=promocion.titulo,
            descripcion=promocion.descripcion,
            tipo_promocion=promocion.tipo_promocion.value,
            estado=promocion.estado.value,
            id_producto=promocion.id_producto,
            porcentaje_descuento=float(promocion.porcentaje_descuento or 0),
            precio_promocional=float(promocion.precio_promocional) if promocion.precio_promocional else None,
            cantidad_minima=promocion.cantidad_minima,
            fecha_inicio=promocion.fecha_inicio,
            fecha_fin=promocion.fecha_fin,
            dias_hasta_vencimiento=promocion.dias_hasta_vencimiento,
            motivo=promocion.motivo,
            ahorro_potencial=float(promocion.ahorro_potencial or 0),
            veces_aplicada=promocion.veces_aplicada,
            fecha_creacion=promocion.fecha_creacion,
            fecha_modificacion=promocion.fecha_modificacion,
            creado_automaticamente=promocion.creado_automaticamente,
            anulado=promocion.anulado,
            nombre_producto=promocion.producto.nombre if promocion.producto else None,
            stock_producto=float(promocion.producto.stock_actual) if promocion.producto else None,
            precio_original=float(promocion.producto.precio_venta) if promocion.producto else None,
            productos_combo=productos_combo
        )

    def get_all(self) -> List[PromocionResponse]:
        promociones = self.repository.get_all()
        return [self._to_response(p) for p in promociones]

    def get_by_id(self, promocion_id: int) -> Optional[PromocionResponse]:
        promocion = self.repository.get_by_id(promocion_id)
        return self._to_response(promocion) if promocion else None

    def get_activas(self) -> List[PromocionResponse]:
        promociones = self.repository.get_activas()
        return [self._to_response(p) for p in promociones]

    def get_sugeridas(self) -> List[PromocionResponse]:
        promociones = self.repository.get_sugeridas()
        return [self._to_response(p) for p in promociones]

    def create(self, data: PromocionCreate) -> PromocionResponse:
        # Generar código si no se proporciona
        codigo = data.codigo_promocion or self.repository.get_next_codigo()
        
        promocion_data = {
            "codigo_promocion": codigo,
            "titulo": data.titulo,
            "descripcion": data.descripcion,
            "tipo_promocion": TipoPromocion(data.tipo_promocion.value),
            "estado": EstadoPromocion.SUGERIDA,  # Inicia como sugerida
            "id_producto": data.id_producto,
            "porcentaje_descuento": data.porcentaje_descuento,
            "precio_promocional": data.precio_promocional,
            "cantidad_minima": data.cantidad_minima,
            "fecha_inicio": data.fecha_inicio,
            "fecha_fin": data.fecha_fin,
            "motivo": data.motivo,
            "creado_automaticamente": False
        }
        
        productos_combo = None
        if data.productos_combo:
            productos_combo = [pc.model_dump() for pc in data.productos_combo]
        
        promocion = self.repository.create(promocion_data, productos_combo)
        return self._to_response(promocion)

    def update(self, promocion_id: int, data: PromocionUpdate) -> Optional[PromocionResponse]:
        update_data = data.model_dump(exclude_unset=True, exclude={'productos_combo'})
        
        # Convertir enums si están presentes
        if 'tipo_promocion' in update_data and update_data['tipo_promocion']:
            update_data['tipo_promocion'] = TipoPromocion(update_data['tipo_promocion'].value)
        if 'estado' in update_data and update_data['estado']:
            update_data['estado'] = EstadoPromocion(update_data['estado'].value)
        
        productos_combo = None
        if data.productos_combo is not None:
            productos_combo = [pc.model_dump() for pc in data.productos_combo]
        
        promocion = self.repository.update(promocion_id, update_data, productos_combo)
        return self._to_response(promocion) if promocion else None

    def activar(self, promocion_id: int) -> Optional[PromocionResponse]:
        promocion = self.repository.cambiar_estado(promocion_id, EstadoPromocion.ACTIVA)
        return self._to_response(promocion) if promocion else None

    def pausar(self, promocion_id: int) -> Optional[PromocionResponse]:
        promocion = self.repository.cambiar_estado(promocion_id, EstadoPromocion.PAUSADA)
        return self._to_response(promocion) if promocion else None

    def cancelar(self, promocion_id: int) -> Optional[PromocionResponse]:
        promocion = self.repository.cambiar_estado(promocion_id, EstadoPromocion.CANCELADA)
        return self._to_response(promocion) if promocion else None

    def finalizar(self, promocion_id: int) -> Optional[PromocionResponse]:
        promocion = self.repository.cambiar_estado(promocion_id, EstadoPromocion.FINALIZADA)
        return self._to_response(promocion) if promocion else None

    def delete(self, promocion_id: int) -> bool:
        return self.repository.delete(promocion_id)

    def generar_sugerencias(self, dias_alerta: int = 7) -> List[SugerenciaPromocion]:
        """
        Genera sugerencias de promociones basadas en productos por vencer.
        
        Args:
            dias_alerta: Número de días antes del vencimiento para generar alertas
        """
        sugerencias = []
        today = date.today()
        
        # Obtener productos con vida útil y stock
        productos = self.db.query(ProductoTerminado).filter(
            ProductoTerminado.anulado == False,
            ProductoTerminado.stock_actual > 0,
            ProductoTerminado.vida_util_dias.isnot(None)
        ).all()

        # Obtener lotes de producción con fechas de vencimiento
        for producto in productos:
            # Buscar el movimiento de producción más antiguo con stock disponible
            movimiento_produccion = self.db.query(MovimientoProductoTerminado).filter(
                MovimientoProductoTerminado.id_producto == producto.id_producto,
                MovimientoProductoTerminado.tipo_movimiento == 'PRODUCCION',
                MovimientoProductoTerminado.anulado == False
            ).order_by(MovimientoProductoTerminado.fecha_movimiento.asc()).first()

            if not movimiento_produccion:
                continue

            # Calcular fecha de vencimiento basada en la fecha de producción y vida útil
            fecha_produccion = movimiento_produccion.fecha_movimiento.date() if hasattr(movimiento_produccion.fecha_movimiento, 'date') else movimiento_produccion.fecha_movimiento
            fecha_vencimiento = fecha_produccion + timedelta(days=producto.vida_util_dias)
            dias_hasta_vencimiento = (fecha_vencimiento - today).days

            if dias_hasta_vencimiento <= dias_alerta and dias_hasta_vencimiento > 0:
                # Determinar urgencia y descuento sugerido
                if dias_hasta_vencimiento <= 1:
                    urgencia = "ALTA"
                    descuento = 50
                    tipo = TipoPromocion.LIQUIDACION
                elif dias_hasta_vencimiento <= 3:
                    urgencia = "ALTA"
                    descuento = 30
                    tipo = TipoPromocion.DESCUENTO
                elif dias_hasta_vencimiento <= 5:
                    urgencia = "MEDIA"
                    descuento = 20
                    tipo = TipoPromocion.DESCUENTO
                else:
                    urgencia = "BAJA"
                    descuento = 15
                    tipo = TipoPromocion.DESCUENTO

                # Calcular ahorro potencial (vs pérdida por merma)
                ahorro_potencial = float(producto.stock_actual) * float(producto.precio_venta) * (1 - descuento/100)

                # Buscar productos complementarios para combo
                productos_combo = self._buscar_complementarios(producto, productos)

                sugerencia = SugerenciaPromocion(
                    id_producto=producto.id_producto,
                    nombre_producto=producto.nombre,
                    stock_actual=float(producto.stock_actual),
                    precio_venta=float(producto.precio_venta),
                    dias_hasta_vencimiento=dias_hasta_vencimiento,
                    tipo_sugerido=tipo,
                    titulo_sugerido=self._generar_titulo(producto.nombre, tipo, dias_hasta_vencimiento),
                    descripcion_sugerida=self._generar_descripcion(producto.nombre, tipo, dias_hasta_vencimiento, descuento),
                    descuento_sugerido=descuento,
                    ahorro_potencial=ahorro_potencial,
                    urgencia=urgencia,
                    productos_combo_sugeridos=productos_combo if tipo != TipoPromocion.LIQUIDACION else None
                )
                sugerencias.append(sugerencia)

        # Ordenar por urgencia y días hasta vencimiento
        sugerencias.sort(key=lambda x: (
            {"ALTA": 0, "MEDIA": 1, "BAJA": 2}[x.urgencia],
            x.dias_hasta_vencimiento
        ))

        return sugerencias

    def _buscar_complementarios(self, producto: ProductoTerminado, todos_productos: List[ProductoTerminado]) -> List[dict]:
        """Busca productos complementarios para crear combos"""
        complementarios = []
        
        for p in todos_productos:
            if p.id_producto != producto.id_producto and float(p.stock_actual) > 0:
                # Agregar como complementario si tiene buen stock
                complementarios.append({
                    "id_producto": p.id_producto,
                    "nombre": p.nombre,
                    "precio_venta": float(p.precio_venta),
                    "stock_actual": float(p.stock_actual)
                })
                
                if len(complementarios) >= 3:  # Máximo 3 sugerencias de combo
                    break
        
        return complementarios if complementarios else None

    def _generar_titulo(self, nombre_producto: str, tipo: TipoPromocion, dias: int) -> str:
        if tipo == TipoPromocion.LIQUIDACION:
            return f"¡LIQUIDACIÓN URGENTE! - {nombre_producto}"
        elif dias <= 3:
            return f"Oferta Especial - {nombre_producto}"
        else:
            return f"Promoción - {nombre_producto}"

    def _generar_descripcion(self, nombre: str, tipo: TipoPromocion, dias: int, descuento: int) -> str:
        if tipo == TipoPromocion.LIQUIDACION:
            return f"Venta de liquidación de {nombre}. ¡Solo queda{'n' if dias > 1 else ''} {dias} día{'s' if dias > 1 else ''}! Precio especial para evitar merma."
        else:
            return f"Aproveche {descuento}% de descuento en {nombre}. Válido por tiempo limitado."

    def crear_desde_sugerencia(self, sugerencia: SugerenciaPromocion, fecha_fin: date = None) -> PromocionResponse:
        """Crea una promoción activa basada en una sugerencia"""
        if fecha_fin is None:
            fecha_fin = date.today() + timedelta(days=sugerencia.dias_hasta_vencimiento)

        promocion_data = {
            "codigo_promocion": self.repository.get_next_codigo(),
            "titulo": sugerencia.titulo_sugerido,
            "descripcion": sugerencia.descripcion_sugerida,
            "tipo_promocion": TipoPromocion(sugerencia.tipo_sugerido.value),
            "estado": EstadoPromocion.ACTIVA,
            "id_producto": sugerencia.id_producto,
            "porcentaje_descuento": sugerencia.descuento_sugerido,
            "cantidad_minima": 1,
            "fecha_inicio": date.today(),
            "fecha_fin": fecha_fin,
            "dias_hasta_vencimiento": sugerencia.dias_hasta_vencimiento,
            "motivo": f"Generada automáticamente - Producto vence en {sugerencia.dias_hasta_vencimiento} días",
            "ahorro_potencial": sugerencia.ahorro_potencial,
            "creado_automaticamente": True
        }

        promocion = self.repository.create(promocion_data)
        return self._to_response(promocion)

    def get_estadisticas(self) -> EstadisticasPromociones:
        """Obtiene estadísticas generales de promociones"""
        todas = self.repository.get_all()
        activas = [p for p in todas if p.estado == EstadoPromocion.ACTIVA]
        sugeridas = [p for p in todas if p.estado == EstadoPromocion.SUGERIDA]
        
        ahorro_total = sum(float(p.ahorro_potencial or 0) for p in activas)
        
        # Contar productos por vencer
        productos_por_vencer = len(self.generar_sugerencias(dias_alerta=7))

        return EstadisticasPromociones(
            total_promociones=len(todas),
            promociones_activas=len(activas),
            promociones_sugeridas=len(sugeridas),
            ahorro_total_estimado=ahorro_total,
            productos_por_vencer=productos_por_vencer
        )
