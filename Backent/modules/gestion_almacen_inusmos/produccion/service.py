from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
from modules.gestion_almacen_inusmos.produccion.repository import ProduccionRepository
from modules.gestion_almacen_inusmos.produccion.schemas import (
    ProduccionRequest,
    ValidacionStockResponse,
    InsumoRequeridoResponse,
    ProduccionResponse,
    HistorialProduccionResponse,
    HistorialProduccionItem,
    TrazabilidadProduccionResponse,
    ProduccionTrazabilidad,
    RecetaTrazabilidad,
    ProductoTerminadoTrazabilidad,
    MovimientoProductoTerminado,
    InsumoConsumidoTrazabilidad
)
from .service_interface import ProduccionServiceInterface


class ProduccionService(ProduccionServiceInterface):
    """
    Service para operaciones de producción.
    Maneja la lógica de negocio para validar stock y ejecutar producción.
    """

    def __init__(self):
        self.repository = ProduccionRepository()

    def validar_stock_receta(
        self, 
        db: Session, 
        id_receta: int, 
        cantidad_batch: Decimal
    ) -> ValidacionStockResponse:
        """
        Valida si hay stock suficiente para producir la cantidad de batch indicada.
        
        Retorna información detallada de cada insumo:
        - Cantidad requerida (cantidad_por_rendimiento * cantidad_batch)
        - Stock disponible
        - Si es suficiente o no
        """
        # Obtener receta con sus insumos
        receta_data = self.repository.get_receta_con_insumos(db, id_receta)
        
        if not receta_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receta no encontrada o no está activa"
            )
        
        receta = receta_data["receta"]
        insumos = receta_data["insumos"]
        
        # Validar cada insumo
        insumos_validados: List[InsumoRequeridoResponse] = []
        puede_producir = True
        
        for insumo in insumos:
            # Si es opcional, no lo validamos (puede omitirse)
            if insumo["es_opcional"]:
                continue
            
            # Calcular cantidad requerida para el batch
            cantidad_requerida = Decimal(str(insumo["cantidad_por_rendimiento"])) * cantidad_batch
            
            # Obtener stock disponible
            stock_disponible = self.repository.get_stock_disponible_insumo(db, insumo["id_insumo"])
            
            # Verificar si es suficiente
            es_suficiente = stock_disponible >= cantidad_requerida
            
            if not es_suficiente:
                puede_producir = False
            
            insumos_validados.append(InsumoRequeridoResponse(
                id_insumo=insumo["id_insumo"],
                codigo_insumo=insumo["codigo_insumo"],
                nombre_insumo=insumo["nombre_insumo"],
                unidad_medida=insumo["unidad_medida"],
                cantidad_requerida=cantidad_requerida,
                stock_disponible=stock_disponible,
                es_suficiente=es_suficiente
            ))
        
        # Construir mensaje
        if puede_producir:
            mensaje = f"Stock suficiente para producir {cantidad_batch} unidades de {receta['nombre_receta']}"
        else:
            insumos_faltantes = [ins.nombre_insumo for ins in insumos_validados if not ins.es_suficiente]
            mensaje = f"Stock insuficiente para los siguientes insumos: {', '.join(insumos_faltantes)}"
        
        return ValidacionStockResponse(
            id_receta=receta["id_receta"],
            nombre_receta=receta["nombre_receta"],
            cantidad_batch=cantidad_batch,
            puede_producir=puede_producir,
            insumos=insumos_validados,
            mensaje=mensaje
        )

    def ejecutar_produccion(self, db: Session, request: ProduccionRequest) -> ProduccionResponse:
        """
        Ejecuta la producción descontando insumos en orden FEFO.
        
        Pasos atómicos:
        1. Valida stock suficiente para todos los insumos
        2. Crea registro en tabla 'produccion' (cabecera)
        3. Descuenta de lotes FEFO y crea movimientos de SALIDA
        4. Incrementa stock de producto terminado
        5. Crea movimiento de ENTRADA en productos terminados
        
        Si falla cualquier paso, revierte toda la transacción.
        """
        # Primero validar stock
        validacion = self.validar_stock_receta(db, request.id_receta, request.cantidad_batch)
        
        if not validacion.puede_producir:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validacion.mensaje
            )
        
        # Obtener receta para el nombre
        receta_data = self.repository.get_receta_con_insumos(db, request.id_receta)
        receta = receta_data["receta"]
        insumos = receta_data["insumos"]
        
        try:
            # PASO 1: Crear registro en tabla produccion
            produccion_creada = self.repository.crear_produccion(
                db=db,
                id_receta=request.id_receta,
                cantidad_batch=request.cantidad_batch,
                id_user=request.id_user,
                observaciones=request.observaciones
            )
            
            id_produccion = produccion_creada["id_produccion"]
            numero_produccion = produccion_creada["numero_produccion"]
            
            total_movimientos = 0
            
            # PASO 2: Descontar cada insumo en orden FEFO
            for insumo in insumos:
                # Saltar opcionales
                if insumo["es_opcional"]:
                    continue
                
                # Calcular cantidad requerida
                cantidad_requerida = Decimal(str(insumo["cantidad_por_rendimiento"])) * request.cantidad_batch
                
                # Descontar usando FEFO y crear movimientos
                # AHORA usa id_produccion como id_documento_origen
                movimientos_creados = self.repository.descontar_insumo_fefo(
                    db=db,
                    id_insumo=insumo["id_insumo"],
                    cantidad_requerida=cantidad_requerida,
                    id_user=request.id_user,
                    id_receta=id_produccion,  # Ahora usamos id_produccion
                    nombre_receta=receta["nombre_receta"]
                )
                
                total_movimientos += movimientos_creados
            
            # PASO 3: Incrementar stock de producto terminado
            id_producto = self.repository.get_id_producto_de_receta(db, request.id_receta)
            
            if id_producto:
                # Calcular cantidad producida
                rendimiento = Decimal(str(receta["rendimiento_producto_terminado"]))
                cantidad_producida = request.cantidad_batch * rendimiento
                
                # Obtener stock anterior
                stock_anterior = self.repository.get_stock_producto_terminado(db, id_producto)
                
                # Incrementar stock
                stock_nuevo = self.repository.incrementar_stock_producto_terminado(
                    db=db,
                    id_producto=id_producto,
                    cantidad=cantidad_producida
                )
                
                # PASO 4: Crear movimiento de ENTRADA en productos terminados
                self.repository.crear_movimiento_producto_terminado(
                    db=db,
                    id_producto=id_producto,
                    cantidad=cantidad_producida,
                    stock_anterior=stock_anterior,
                    stock_nuevo=stock_nuevo,
                    id_user=request.id_user,
                    id_produccion=id_produccion,
                    observaciones=f"Entrada por producción {numero_produccion} de {receta['nombre_receta']}"
                )
            else:
                cantidad_producida = Decimal('0')
            
            # Commit de toda la transacción
            db.commit()
            
            # Resetear contador de movimientos
            self.repository._reset_contador_movimientos()
            
            return ProduccionResponse(
                success=True,
                mensaje=f"Producción {numero_produccion} ejecutada correctamente. Se produjeron {cantidad_producida} unidades de {receta['nombre_receta']}",
                id_produccion=id_produccion,
                numero_produccion=numero_produccion,
                id_receta=request.id_receta,
                nombre_receta=receta["nombre_receta"],
                cantidad_batch=request.cantidad_batch,
                cantidad_producida=cantidad_producida,
                total_movimientos_creados=total_movimientos
            )
            
        except Exception as e:
            # Resetear contador de movimientos en caso de error
            self.repository._reset_contador_movimientos()
            
            # Revertir toda la transacción si hay error
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al ejecutar producción: {str(e)}. Se revirtieron todos los cambios."
            )

    def get_historial_producciones(
        self, 
        db: Session, 
        limit: int = 50, 
        offset: int = 0
    ) -> HistorialProduccionResponse:
        """
        Obtiene el historial de producciones realizadas.
        """
        producciones = self.repository.get_historial_producciones(db, limit, offset)
        
        items = [
            HistorialProduccionItem(
                id_produccion=p["id_produccion"],
                numero_produccion=p["numero_produccion"],
                id_receta=p["id_receta"],
                codigo_receta=p["codigo_receta"],
                nombre_receta=p["nombre_receta"],
                nombre_producto=p["nombre_producto"],
                cantidad_batch=p["cantidad_batch"],
                rendimiento_producto_terminado=p["rendimiento_producto_terminado"],
                cantidad_producida=p["cantidad_producida"],
                fecha_produccion=p["fecha_produccion"],
                id_user=p["id_user"],
                nombre_usuario=p["nombre_usuario"],
                observaciones=p["observaciones"],
                anulado=p["anulado"]
            )
            for p in producciones
        ]
        
        return HistorialProduccionResponse(
            total=len(items),
            producciones=items
        )

    def get_trazabilidad_produccion(
        self, 
        db: Session, 
        id_produccion: int
    ) -> TrazabilidadProduccionResponse:
        """
        Obtiene la trazabilidad completa de una producción.
        """
        trazabilidad = self.repository.get_trazabilidad_produccion(db, id_produccion)
        
        if not trazabilidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producción con ID {id_produccion} no encontrada"
            )
        
        # Construir respuesta
        produccion_data = trazabilidad["produccion"]
        receta_data = trazabilidad["receta"]
        producto_data = trazabilidad["producto_terminado"]
        insumos_data = trazabilidad["insumos_consumidos"]
        
        # Mapear movimiento de entrada del producto terminado
        mov_entrada = None
        if producto_data.get("movimiento_entrada"):
            mov = producto_data["movimiento_entrada"]
            mov_entrada = MovimientoProductoTerminado(
                id_movimiento=mov.get("id_movimiento"),
                numero_movimiento=mov.get("numero_movimiento"),
                cantidad=mov.get("cantidad"),
                fecha_movimiento=mov.get("fecha_movimiento")
            )
        
        return TrazabilidadProduccionResponse(
            produccion=ProduccionTrazabilidad(
                id_produccion=produccion_data["id_produccion"],
                numero_produccion=produccion_data["numero_produccion"],
                fecha_produccion=produccion_data["fecha_produccion"],
                cantidad_batch=produccion_data["cantidad_batch"],
                cantidad_producida=produccion_data["cantidad_producida"],
                usuario=produccion_data["usuario"],
                observaciones=produccion_data["observaciones"],
                anulado=produccion_data["anulado"]
            ),
            receta=RecetaTrazabilidad(
                id_receta=receta_data["id_receta"],
                codigo_receta=receta_data["codigo_receta"],
                nombre_receta=receta_data["nombre_receta"],
                rendimiento_producto_terminado=receta_data["rendimiento_producto_terminado"]
            ),
            producto_terminado=ProductoTerminadoTrazabilidad(
                id_producto=producto_data["id_producto"],
                nombre_producto=producto_data["nombre_producto"],
                movimiento_entrada=mov_entrada
            ),
            insumos_consumidos=[
                InsumoConsumidoTrazabilidad(
                    id_movimiento=ins["id_movimiento"],
                    numero_movimiento=ins["numero_movimiento"],
                    id_insumo=ins["id_insumo"],
                    codigo_insumo=ins["codigo_insumo"],
                    nombre_insumo=ins["nombre_insumo"],
                    unidad_medida=ins["unidad_medida"],
                    id_lote=ins["id_lote"],
                    fecha_vencimiento_lote=ins["fecha_vencimiento_lote"],
                    cantidad_consumida=ins["cantidad_consumida"],
                    stock_anterior_lote=ins["stock_anterior_lote"],
                    stock_nuevo_lote=ins["stock_nuevo_lote"],
                    fecha_movimiento=ins["fecha_movimiento"]
                )
                for ins in insumos_data
            ],
            total_lotes_consumidos=trazabilidad["total_lotes_consumidos"]
        )
