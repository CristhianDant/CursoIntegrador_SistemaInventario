from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import datetime, date, timedelta
from loguru import logger

from modules.orden_de_compra.schemas import (
    OrdenDeCompra, OrdenDeCompraCreate, OrdenDeCompraUpdate,
    SugerenciaCompraResponse, ItemSugerenciaCompra, ProveedorSugerencia,
    GenerarOrdenDesdesugerenciaRequest, EnviarEmailProveedorRequest,
    EnviarEmailProveedorResponse, OrdenDeCompraDetalleCreate
)
from modules.orden_de_compra.repository import OrdenDeCompraRepository
from modules.orden_de_compra.service_interface import OrdenDeCompraServiceInterface
from modules.email_service.service import EmailService
from modules.email_service.schemas import EmailCreate
from enums.monedas import MonedaEnum
from enums.estado import EstadoEnum

class OrdenDeCompraService(OrdenDeCompraServiceInterface):
    def __init__(self):
        self.repository = OrdenDeCompraRepository()
        self.email_service = EmailService()

    def get_all(self, db: Session, activas_solo: bool = True) -> List[OrdenDeCompra]:
        return self.repository.get_all(db, activas_solo=activas_solo)

    def get_by_id(self, db: Session, orden_id: int) -> OrdenDeCompra:
        orden = self.repository.get_by_id(db, orden_id)
        if not orden:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        return orden

    def create(self, db: Session, orden: OrdenDeCompraCreate) -> OrdenDeCompra:
        return self.repository.create(db, orden)

    def update(self, db: Session, orden_id: int, orden: OrdenDeCompraUpdate) -> OrdenDeCompra:
        orden_actualizada = self.repository.update(db, orden_id, orden)
        if not orden_actualizada:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        return orden_actualizada

    def delete(self, db: Session, orden_id: int) -> dict:
        if not self.repository.delete(db, orden_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orden de compra no encontrada")
        return {"message": "Orden de compra anulada correctamente"}

    # ==================== SUGERENCIAS DE COMPRA (FC-10) ====================
    
    def generar_sugerencias_compra(
        self,
        db: Session,
        dias_proyeccion: int = 7,
        urgencia: Optional[str] = None,
        id_proveedor: Optional[int] = None
    ) -> SugerenciaCompraResponse:
        """
        Genera sugerencias de compra basadas en:
        - Stock actual < stock mínimo
        - Días de stock restante
        - Vencimientos próximos (7 días)
        """
        # Obtener datos necesarios
        stock_insumos = self.repository.obtener_stock_actual_insumos(db)
        consumo_diario = self.repository.obtener_consumo_promedio_insumos(db, dias=30)
        cantidad_por_vencer = self.repository.obtener_cantidad_por_vencer(db, dias_limite=7)
        ultimos_precios = self.repository.obtener_ultimo_precio_insumos(db)
        proveedores_por_insumo = self.repository.obtener_proveedor_por_insumo(db)
        
        items_sugerencia: List[ItemSugerenciaCompra] = []
        
        for insumo in stock_insumos:
            id_insumo = insumo['id_insumo']
            stock_actual = insumo['stock_actual']
            stock_minimo = insumo['stock_minimo']
            
            # Obtener consumo diario (0 si no hay datos)
            consumo = consumo_diario.get(id_insumo, Decimal('0'))
            
            # Calcular días de stock restante
            if consumo > 0:
                dias_stock = stock_actual / consumo
            else:
                dias_stock = Decimal('999')  # Sin consumo = stock infinito
            
            # Determinar si necesita reposición
            necesita_compra = False
            razon = ""
            
            # Criterio 1: Stock bajo mínimo
            if stock_actual < stock_minimo:
                necesita_compra = True
                razon = f"Stock ({stock_actual}) bajo mínimo ({stock_minimo})"
            
            # Criterio 2: Días de stock restante < días proyección
            elif dias_stock < Decimal(str(dias_proyeccion)):
                necesita_compra = True
                razon = f"Solo {dias_stock:.1f} días de stock restante"
            
            # Criterio 3: Cantidad significativa por vencer
            cantidad_vence = cantidad_por_vencer.get(id_insumo, Decimal('0'))
            if cantidad_vence > 0 and cantidad_vence >= stock_actual * Decimal('0.3'):
                necesita_compra = True
                razon = f"{cantidad_vence} unidades vencen en 7 días"
            
            if not necesita_compra:
                continue
            
            # Calcular cantidad sugerida
            if consumo > 0:
                cantidad_sugerida = consumo * Decimal(str(dias_proyeccion))
                # Asegurar que sea al menos el déficit
                deficit = max(Decimal('0'), stock_minimo - stock_actual)
                cantidad_sugerida = max(cantidad_sugerida, deficit)
            else:
                # Sin consumo histórico, sugerir llegar al mínimo
                cantidad_sugerida = max(Decimal('0'), stock_minimo - stock_actual)
            
            # Redondear hacia arriba
            cantidad_sugerida = cantidad_sugerida.quantize(Decimal('0.01'))
            
            if cantidad_sugerida <= 0:
                continue
            
            # Determinar urgencia (rojo = inmediata si < 7 días de stock)
            es_urgente = dias_stock < Decimal('7') or stock_actual == 0
            urgencia_item = "inmediata" if es_urgente else "normal"
            
            # Filtrar por urgencia si se especificó
            if urgencia:
                if urgencia == "inmediata" and not es_urgente:
                    continue
                if urgencia == "normal" and es_urgente:
                    continue
            
            # Obtener precio y proveedor
            ultimo_precio = ultimos_precios.get(id_insumo)
            proveedor_info = proveedores_por_insumo.get(id_insumo, {})
            
            # Filtrar por proveedor si se especificó
            if id_proveedor and proveedor_info.get('id_proveedor') != id_proveedor:
                continue
            
            subtotal = cantidad_sugerida * ultimo_precio if ultimo_precio else None
            
            item = ItemSugerenciaCompra(
                id_insumo=id_insumo,
                codigo=insumo['codigo'],
                nombre=insumo['nombre'],
                unidad_medida=insumo['unidad_medida'],
                categoria=insumo['categoria'],
                stock_actual=stock_actual,
                stock_minimo=stock_minimo,
                deficit=max(Decimal('0'), stock_minimo - stock_actual),
                consumo_diario_promedio=consumo,
                dias_stock_restante=dias_stock if dias_stock < 999 else Decimal('0'),
                cantidad_por_vencer=cantidad_vence,
                cantidad_sugerida=cantidad_sugerida,
                urgencia=urgencia_item,
                razon=razon,
                ultimo_precio=ultimo_precio,
                subtotal_estimado=subtotal
            )
            
            # Agregar info del proveedor al item (para agrupar después)
            item._proveedor_info = proveedor_info
            items_sugerencia.append(item)
        
        # Agrupar por proveedor
        proveedores_dict: Dict[int, ProveedorSugerencia] = {}
        items_sin_proveedor: List[ItemSugerenciaCompra] = []
        
        for item in items_sugerencia:
            proveedor_info = getattr(item, '_proveedor_info', {})
            delattr(item, '_proveedor_info')
            
            if proveedor_info and proveedor_info.get('id_proveedor'):
                prov_id = proveedor_info['id_proveedor']
                
                if prov_id not in proveedores_dict:
                    proveedores_dict[prov_id] = ProveedorSugerencia(
                        id_proveedor=prov_id,
                        nombre_proveedor=proveedor_info.get('nombre', 'Sin nombre'),
                        email=proveedor_info.get('email', ''),
                        telefono=proveedor_info.get('telefono', ''),
                        total_items=0,
                        total_estimado=Decimal('0'),
                        items=[]
                    )
                
                proveedores_dict[prov_id].items.append(item)
                proveedores_dict[prov_id].total_items += 1
                if item.subtotal_estimado:
                    proveedores_dict[prov_id].total_estimado += item.subtotal_estimado
            else:
                items_sin_proveedor.append(item)
        
        # Calcular totales
        total_items = len(items_sugerencia)
        total_urgentes = sum(1 for i in items_sugerencia if i.urgencia == "inmediata")
        total_estimado = sum(
            i.subtotal_estimado for i in items_sugerencia 
            if i.subtotal_estimado
        ) or Decimal('0')
        
        return SugerenciaCompraResponse(
            fecha_generacion=datetime.now(),
            dias_proyeccion=dias_proyeccion,
            total_items=total_items,
            total_items_urgentes=total_urgentes,
            total_estimado=total_estimado,
            por_proveedor=list(proveedores_dict.values()),
            todos_items=items_sugerencia
        )
    
    def generar_orden_desde_sugerencia(
        self,
        db: Session,
        request: GenerarOrdenDesdesugerenciaRequest
    ) -> OrdenDeCompra:
        """Genera una orden de compra a partir de items sugeridos."""
        
        # Validar proveedor
        proveedor = self.repository.obtener_proveedor_por_id(db, request.id_proveedor)
        if not proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {request.id_proveedor} no encontrado"
            )
        
        # Construir detalles
        detalles = []
        sub_total = Decimal('0')
        
        for item in request.items:
            cantidad = Decimal(str(item['cantidad']))
            precio = Decimal(str(item['precio_unitario']))
            item_subtotal = cantidad * precio
            sub_total += item_subtotal
            
            detalles.append(OrdenDeCompraDetalleCreate(
                id_insumo=item['id_insumo'],
                cantidad=cantidad,
                precio_unitario=precio,
                descuento_unitario=Decimal('0'),
                sub_total=item_subtotal,
                observaciones=None
            ))
        
        # Calcular IGV (18%)
        igv = sub_total * Decimal('0.18')
        total = sub_total + igv
        
        # Generar número de orden
        numero_orden = self.repository.generar_numero_orden(db)
        
        # Crear orden
        orden_create = OrdenDeCompraCreate(
            numero_orden=numero_orden,
            id_proveedor=request.id_proveedor,
            fecha_entrega_esperada=request.fecha_entrega_esperada,
            moneda=MonedaEnum.PEN,
            tipo_cambio=Decimal('1'),
            sub_total=sub_total,
            descuento=Decimal('0'),
            igv=igv,
            total=total,
            estado=EstadoEnum.PENDIENTE,
            observaciones=request.observaciones or "Generada desde sugerencia automática",
            id_user_creador=request.id_user_creador,
            detalles=detalles
        )
        
        return self.repository.create(db, orden_create)
    
    def enviar_email_proveedor(
        self,
        db: Session,
        request: EnviarEmailProveedorRequest
    ) -> EnviarEmailProveedorResponse:
        """Envía un email al proveedor con la lista de compras sugerida."""
        
        # Obtener proveedor
        proveedor = self.repository.obtener_proveedor_por_id(db, request.id_proveedor)
        if not proveedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Proveedor con ID {request.id_proveedor} no encontrado"
            )
        
        if not proveedor['email']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El proveedor {proveedor['nombre']} no tiene email registrado"
            )
        
        # Obtener nombre de empresa
        from modules.empresa.model import Empresa
        empresa = db.query(Empresa).filter(Empresa.estado == True).first()
        nombre_empresa = empresa.nombre_empresa if empresa else "Sistema de Inventario"
        
        # Construir HTML del email
        html_content = self._construir_email_html(
            nombre_empresa=nombre_empresa,
            proveedor=proveedor,
            items=request.items,
            mensaje_adicional=request.mensaje_adicional
        )
        
        # Crear email
        email_data = EmailCreate(
            destinatario=proveedor['email'],
            asunto=f"Solicitud de Cotización - {nombre_empresa}",
            cuerpo_html=html_content
        )
        
        # Enviar o encolar
        enviado, mensaje = self.email_service.enviar_o_encolar(db, email_data)
        
        return EnviarEmailProveedorResponse(
            enviado=enviado,
            mensaje=mensaje,
            email_destino=proveedor['email'],
            fecha_envio=datetime.now() if enviado else None
        )
    
    def _construir_email_html(
        self,
        nombre_empresa: str,
        proveedor: Dict[str, Any],
        items: List[Dict],
        mensaje_adicional: Optional[str] = None
    ) -> str:
        """Construye el HTML del email para el proveedor."""
        
        # Construir filas de la tabla
        filas_html = ""
        total = Decimal('0')
        
        for item in items:
            cantidad = Decimal(str(item.get('cantidad', 0)))
            precio = Decimal(str(item.get('ultimo_precio', 0))) if item.get('ultimo_precio') else Decimal('0')
            subtotal = cantidad * precio
            total += subtotal
            
            filas_html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{item.get('nombre', 'N/A')}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{cantidad}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{item.get('unidad_medida', '')}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">S/ {precio:.2f}</td>
                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">S/ {subtotal:.2f}</td>
            </tr>
            """
        
        mensaje_extra = ""
        if mensaje_adicional:
            mensaje_extra = f"""
            <div style="margin: 20px 0; padding: 15px; background-color: #f0f0f0; border-radius: 5px;">
                <strong>Mensaje adicional:</strong><br>
                {mensaje_adicional}
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Solicitud de Cotización</title>
        </head>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 700px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #333; margin: 0;">{nombre_empresa}</h1>
                    <p style="color: #666; margin: 5px 0;">Solicitud de Cotización</p>
                </div>
                
                <p>Estimado(a) <strong>{proveedor['nombre']}</strong>,</p>
                
                <p>Por medio del presente, solicitamos cotización para los siguientes insumos:</p>
                
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <thead>
                        <tr style="background-color: #4CAF50; color: white;">
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Insumo</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Cantidad</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: center;">Unidad</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: right;">Precio Ref.</th>
                            <th style="padding: 12px; border: 1px solid #ddd; text-align: right;">Subtotal Ref.</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_html}
                    </tbody>
                    <tfoot>
                        <tr style="background-color: #f9f9f9; font-weight: bold;">
                            <td colspan="4" style="padding: 12px; border: 1px solid #ddd; text-align: right;">Total Estimado:</td>
                            <td style="padding: 12px; border: 1px solid #ddd; text-align: right;">S/ {total:.2f}</td>
                        </tr>
                    </tfoot>
                </table>
                
                {mensaje_extra}
                
                <p>Agradecemos nos envíen su cotización formal a la brevedad posible.</p>
                
                <p>Saludos cordiales,<br>
                <strong>{nombre_empresa}</strong></p>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                
                <p style="color: #999; font-size: 12px; text-align: center;">
                    Este mensaje fue generado automáticamente por el Sistema de Inventario.<br>
                    Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
                </p>
            </div>
        </body>
        </html>
        """
        
        return html

