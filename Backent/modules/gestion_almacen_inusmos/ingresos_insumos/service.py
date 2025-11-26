from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
from modules.gestion_almacen_inusmos.ingresos_insumos.schemas import (
    IngresoProducto, IngresoProductoCreate, IngresoProductoUpdate, 
    InsumoLotesFefoResponse, IngresoDetalleFefoResponse,
    InsumoLotesConTotalResponse, LoteConProveedorResponse
)
from modules.gestion_almacen_inusmos.ingresos_insumos.repository import IngresoProductoRepository
from modules.gestion_almacen_inusmos.ingresos_insumos.service_interface import IngresoProductoServiceInterface
from modules.insumo.model import Insumo

class IngresoProductoService(IngresoProductoServiceInterface):
    def __init__(self):
        self.repository = IngresoProductoRepository()

    def get_all(self, db: Session) -> List[IngresoProducto]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, ingreso_id: int) -> IngresoProducto:
        ingreso = self.repository.get_by_id(db, ingreso_id)
        if not ingreso:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingreso de producto no encontrado")
        return ingreso

    def create(self, db: Session, ingreso: IngresoProductoCreate) -> IngresoProducto:
        return self.repository.create(db, ingreso)

    def update(self, db: Session, ingreso_id: int, ingreso: IngresoProductoUpdate) -> IngresoProducto:
        ingreso_actualizado = self.repository.update(db, ingreso_id, ingreso)
        if not ingreso_actualizado:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingreso de producto no encontrado")
        return ingreso_actualizado

    def delete(self, db: Session, ingreso_id: int) -> dict:
        if not self.repository.delete(db, ingreso_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingreso de producto no encontrado")
        return {"message": "Ingreso de producto anulado correctamente"}

    def get_lotes_fefo(self, db: Session, id_insumo: int) -> InsumoLotesFefoResponse:
        """Obtiene los lotes FEFO de un insumo con su información
        Retorna el insumo y sus lotes ordenados por FEFO
        """
        # Obtener información del insumo
        insumo = db.query(Insumo).filter(Insumo.id_insumo == id_insumo, Insumo.anulado == False).first()
        if not insumo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
        
        # Obtener lotes FEFO del insumo
        lotes = self.repository.get_lotes_fefo(db, id_insumo)
        
        # Construir respuesta
        return InsumoLotesFefoResponse(
            id_insumo=insumo.id_insumo,
            nombre_insumo=insumo.nombre,
            lotes=[IngresoDetalleFefoResponse.from_orm(lote) for lote in lotes]
        )

    def get_lotes_fefo_con_total(self, db: Session, id_insumo: int) -> InsumoLotesConTotalResponse:
        """
        Obtiene los lotes FEFO de un insumo con información del proveedor,
        el total de cantidad_restante y la cantidad de lotes disponibles.
        
        Retorna:
        - Información del insumo (id, código, nombre, unidad de medida)
        - Total de cantidad_restante (suma de todos los lotes con stock)
        - Cantidad de lotes disponibles
        - Lista de lotes con datos del proveedor e ingreso, ordenados por FEFO
        """
        # Obtener información del insumo
        insumo = db.query(Insumo).filter(
            Insumo.id_insumo == id_insumo, 
            Insumo.anulado == False
        ).first()
        
        if not insumo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Insumo no encontrado"
            )
        
        # Obtener lotes FEFO con información del proveedor usando raw SQL
        lotes_data = self.repository.get_lotes_fefo_con_proveedor(db, id_insumo)
        
        # Calcular el total de cantidad_restante
        total_cantidad_restante = sum(
            Decimal(str(lote["cantidad_restante"])) for lote in lotes_data
        )
        
        # Construir lista de lotes con el schema correspondiente
        lotes_response = [
            LoteConProveedorResponse(
                id_ingreso_detalle=lote["id_ingreso_detalle"],
                id_ingreso=lote["id_ingreso"],
                cantidad_ingresada=lote["cantidad_ingresada"],
                cantidad_restante=lote["cantidad_restante"],
                precio_unitario=lote["precio_unitario"],
                subtotal=lote["subtotal"],
                fecha_vencimiento=lote["fecha_vencimiento"],
                numero_ingreso=lote["numero_ingreso"],
                fecha_ingreso=lote["fecha_ingreso"],
                nombre_proveedor=lote["nombre_proveedor"]
            )
            for lote in lotes_data
        ]
        
        # Construir respuesta final
        return InsumoLotesConTotalResponse(
            id_insumo=insumo.id_insumo,
            codigo_insumo=insumo.codigo,
            nombre_insumo=insumo.nombre,
            unidad_medida=insumo.unidad_medida.value if hasattr(insumo.unidad_medida, 'value') else str(insumo.unidad_medida),
            total_cantidad_restante=total_cantidad_restante,
            cantidad_lotes=len(lotes_response),
            lotes=lotes_response
        )

