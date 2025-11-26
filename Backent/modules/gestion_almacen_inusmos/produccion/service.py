from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
from modules.gestion_almacen_inusmos.produccion.repository import ProduccionRepository
from modules.gestion_almacen_inusmos.produccion.schemas import (
    ProduccionRequest,
    ValidacionStockResponse,
    InsumoRequeridoResponse,
    ProduccionResponse
)


class ProduccionService:
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
        
        1. Valida stock suficiente para todos los insumos
        2. Descuenta de lotes FEFO
        3. Crea movimientos de SALIDA
        
        Si falla cualquier insumo, revierte toda la transacción.
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
            total_movimientos = 0
            
            # Descontar cada insumo en orden FEFO
            for insumo in insumos:
                # Saltar opcionales
                if insumo["es_opcional"]:
                    continue
                
                # Calcular cantidad requerida
                cantidad_requerida = Decimal(str(insumo["cantidad_por_rendimiento"])) * request.cantidad_batch
                
                # Descontar usando FEFO y crear movimientos
                movimientos_creados = self.repository.descontar_insumo_fefo(
                    db=db,
                    id_insumo=insumo["id_insumo"],
                    cantidad_requerida=cantidad_requerida,
                    id_user=request.id_user,
                    id_receta=request.id_receta,
                    nombre_receta=receta["nombre_receta"]
                )
                
                total_movimientos += movimientos_creados
            
            # Commit de toda la transacción
            db.commit()
            
            return ProduccionResponse(
                success=True,
                mensaje=f"Insumos despachados correctamente para la producción de {request.cantidad_batch} unidades de {receta['nombre_receta']}",
                id_receta=request.id_receta,
                nombre_receta=receta["nombre_receta"],
                cantidad_batch=request.cantidad_batch,
                total_movimientos_creados=total_movimientos
            )
            
        except Exception as e:
            # Revertir toda la transacción si hay error
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al ejecutar producción: {str(e)}. Se revirtieron todos los cambios."
            )
