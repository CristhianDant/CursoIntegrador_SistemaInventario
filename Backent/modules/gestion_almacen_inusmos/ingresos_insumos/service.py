from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from modules.gestion_almacen_inusmos.ingresos_insumos.schemas import IngresoProducto, IngresoProductoCreate, IngresoProductoUpdate, InsumoLotesFefoResponse, IngresoDetalleFefoResponse
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

