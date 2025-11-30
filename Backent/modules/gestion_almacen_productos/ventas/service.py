from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
from datetime import date, datetime
from modules.gestion_almacen_productos.ventas.service_interface import VentasServiceInterface
from modules.gestion_almacen_productos.ventas.repository import VentasRepository
from modules.gestion_almacen_productos.ventas.schemas import (
    RegistrarVentaRequest,
    VentaResponse,
    VentaResumenResponse,
    VentaDetalleResponse,
    ProductoDisponibleResponse,
    VentasDelDiaResponse
)


class VentasService(VentasServiceInterface):
    """Servicio de lógica de negocio para ventas."""
    
    def __init__(self):
        self.repository = VentasRepository()
    
    def registrar_venta(
        self,
        db: Session,
        request: RegistrarVentaRequest,
        id_user: int
    ) -> VentaResponse:
        """
        Registra una venta completa con descuento automático de stock.
        Transacción atómica: si falla algo, se hace rollback.
        """
        try:
            # 1. VALIDAR STOCK DISPONIBLE
            for item in request.items:
                producto = self.repository.get_producto_info(db, item.id_producto)
                if not producto:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Producto con ID {item.id_producto} no encontrado"
                    )
                
                stock_actual = self.repository.get_stock_producto(db, item.id_producto)
                if stock_actual < item.cantidad:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Stock insuficiente para {producto['nombre']}. "
                               f"Disponible: {stock_actual}, Solicitado: {item.cantidad}"
                    )
            
            # 2. CALCULAR TOTALES
            total = Decimal("0")
            items_calculados = []
            
            for item in request.items:
                # Calcular descuento
                descuento = item.precio_unitario * (item.descuento_porcentaje / Decimal("100"))
                precio_con_descuento = item.precio_unitario - descuento
                subtotal = precio_con_descuento * item.cantidad
                total += subtotal
                
                items_calculados.append({
                    "item": item,
                    "subtotal": subtotal
                })
            
            # 3. CREAR VENTA
            numero_venta = self.repository.generar_numero_venta(db)
            venta_data = self.repository.crear_venta(
                db=db,
                numero_venta=numero_venta,
                total=total,
                metodo_pago=request.metodo_pago,
                id_user=id_user,
                observaciones=request.observaciones
            )
            
            id_venta = venta_data["id_venta"]
            
            # 4. CREAR DETALLES Y DESCONTAR STOCK
            detalles_response = []
            
            for item_calc in items_calculados:
                item = item_calc["item"]
                subtotal = item_calc["subtotal"]
                
                # Crear detalle
                id_detalle = self.repository.crear_detalle_venta(
                    db=db,
                    id_venta=id_venta,
                    id_producto=item.id_producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    descuento_porcentaje=item.descuento_porcentaje,
                    subtotal=subtotal
                )
                
                # Obtener info del producto
                producto = self.repository.get_producto_info(db, item.id_producto)
                stock_anterior = self.repository.get_stock_producto(db, item.id_producto)
                
                # Descontar stock
                stock_nuevo = self.repository.descontar_stock_producto(
                    db=db,
                    id_producto=item.id_producto,
                    cantidad=item.cantidad
                )
                
                # Crear movimiento de salida
                self._crear_movimiento_salida(
                    db=db,
                    id_producto=item.id_producto,
                    cantidad=item.cantidad,
                    id_user=id_user,
                    id_venta=id_venta,
                    numero_venta=numero_venta
                )
                
                # Preparar respuesta del detalle
                detalles_response.append(VentaDetalleResponse(
                    id_detalle=id_detalle,
                    id_producto=item.id_producto,
                    nombre_producto=producto["nombre"],
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    descuento_porcentaje=item.descuento_porcentaje,
                    subtotal=subtotal
                ))
            
            # 5. COMMIT DE LA TRANSACCIÓN
            db.commit()
            
            # 6. PREPARAR RESPUESTA
            return VentaResponse(
                id_venta=id_venta,
                numero_venta=numero_venta,
                fecha_venta=venta_data["fecha_venta"],
                total=total,
                metodo_pago=request.metodo_pago,
                id_user=id_user,
                nombre_usuario="Usuario",  # Se obtiene del contexto JWT
                observaciones=request.observaciones,
                anulado=False,
                detalles=detalles_response
            )
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar venta: {str(e)}"
            )
    
    def get_venta_por_id(self, db: Session, id_venta: int) -> VentaResponse:
        """Obtiene una venta por ID."""
        venta_data = self.repository.get_venta_por_id(db, id_venta)
        
        if not venta_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Venta con ID {id_venta} no encontrada"
            )
        
        detalles = [
            VentaDetalleResponse(**detalle)
            for detalle in venta_data["detalles"]
        ]
        
        return VentaResponse(
            id_venta=venta_data["id_venta"],
            numero_venta=venta_data["numero_venta"],
            fecha_venta=venta_data["fecha_venta"],
            total=venta_data["total"],
            metodo_pago=venta_data["metodo_pago"],
            id_user=venta_data["id_user"],
            nombre_usuario=venta_data["nombre_usuario"],
            observaciones=venta_data["observaciones"],
            anulado=venta_data["anulado"],
            detalles=detalles
        )
    
    def get_ventas_del_dia(self, db: Session, fecha: date) -> VentasDelDiaResponse:
        """Obtiene ventas del día."""
        ventas = self.repository.get_ventas_del_dia(db, fecha)
        
        total_ventas = len(ventas)
        monto_total = sum((v["total"] for v in ventas if not v["anulado"]), Decimal("0"))

        ventas_response = [
            VentaResumenResponse(**venta)
            for venta in ventas
        ]
        
        return VentasDelDiaResponse(
            fecha=datetime.combine(fecha, datetime.min.time()),
            total_ventas=total_ventas,
            monto_total=monto_total,
            ventas=ventas_response
        )
    
    def get_productos_disponibles(self, db: Session) -> List[ProductoDisponibleResponse]:
        """
        Obtiene productos disponibles con descuento sugerido según antigüedad.
        Implementa FC-09: Descuento automático productos día anterior.
        """
        productos = self.repository.get_productos_disponibles(db)
        hoy = date.today()
        
        resultado = []
        
        for producto in productos:
            # Obtener última producción
            ultima_prod = self.repository.get_ultima_produccion_producto(
                db, 
                producto["id_producto"]
            )
            
            dias_antiguedad = None
            descuento_sugerido = Decimal("0")
            
            if ultima_prod:
                fecha_prod = ultima_prod["fecha_produccion"].date()
                dias_antiguedad = (hoy - fecha_prod).days
                
                # Calcular descuento según antigüedad (FC-09)
                if dias_antiguedad == 1:
                    descuento_sugerido = Decimal("30")  # 30%
                elif dias_antiguedad == 2:
                    descuento_sugerido = Decimal("50")  # 50%
                elif dias_antiguedad >= 3:
                    descuento_sugerido = Decimal("70")  # 70%
            
            resultado.append(ProductoDisponibleResponse(
                id_producto=producto["id_producto"],
                codigo_producto=producto["codigo_producto"],
                nombre=producto["nombre"],
                descripcion=producto["descripcion"],
                stock_actual=producto["stock_actual"],
                precio_venta=producto["precio_venta"],
                dias_desde_produccion=dias_antiguedad,
                descuento_sugerido=descuento_sugerido
            ))
        
        return resultado
    
    def anular_venta(self, db: Session, id_venta: int, id_user: int) -> VentaResponse:
        """
        Anula una venta y restaura el stock.
        """
        try:
            # Obtener venta
            venta_data = self.repository.get_venta_por_id(db, id_venta)
            
            if not venta_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Venta con ID {id_venta} no encontrada"
                )
            
            if venta_data["anulado"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La venta ya está anulada"
                )
            
            # Restaurar stock de cada producto
            for detalle in venta_data["detalles"]:
                stock_anterior = self.repository.get_stock_producto(
                    db, 
                    detalle["id_producto"]
                )
                
                # Incrementar stock (restaurar)
                nuevo_stock = self.repository.incrementar_stock_producto(
                    db=db,
                    id_producto=detalle["id_producto"],
                    cantidad=detalle["cantidad"]
                )

                # Crear movimiento de entrada (compensación)
                self._crear_movimiento_entrada_compensacion(
                    db=db,
                    id_producto=detalle["id_producto"],
                    cantidad=detalle["cantidad"],
                    id_user=id_user,
                    id_venta=id_venta,
                    numero_venta=venta_data["numero_venta"]
                )
            
            # Marcar venta como anulada
            self.repository.anular_venta(db, id_venta)
            
            db.commit()
            
            # Retornar venta actualizada
            return self.get_venta_por_id(db, id_venta)
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al anular venta: {str(e)}"
            )
    
    # ============================================================
    # MÉTODOS PRIVADOS
    # ============================================================
    
    def _crear_movimiento_salida(
        self,
        db: Session,
        id_producto: int,
        cantidad: Decimal,
        id_user: int,
        id_venta: int,
        numero_venta: str
    ):
        """Crea un movimiento de SALIDA en movimiento_productos_terminados."""
        self.repository.crear_movimiento_salida(
            db=db,
            id_producto=id_producto,
            cantidad=cantidad,
            id_user=id_user,
            id_venta=id_venta,
            numero_venta=numero_venta
        )

    def _crear_movimiento_entrada_compensacion(
        self,
        db: Session,
        id_producto: int,
        cantidad: Decimal,
        id_user: int,
        id_venta: int,
        numero_venta: str
    ):
        """Crea un movimiento de ENTRADA por anulación de venta."""
        self.repository.crear_movimiento_entrada_compensacion(
            db=db,
            id_producto=id_producto,
            cantidad=cantidad,
            id_user=id_user,
            id_venta=id_venta,
            numero_venta=numero_venta
        )
