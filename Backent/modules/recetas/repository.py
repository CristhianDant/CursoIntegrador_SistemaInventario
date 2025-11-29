from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from modules.recetas.model import Receta, RecetaDetalle
from modules.recetas.schemas import RecetaCreate, RecetaUpdate
from modules.recetas.repository_interface import RecetaRepositoryInterface

class RecetaRepository(RecetaRepositoryInterface):
    def get_all(self, db: Session) -> List[Receta]:
        return db.query(Receta).options(joinedload(Receta.detalles)).filter(Receta.anulado == False).all()

    def get_by_id(self, db: Session, receta_id: int) -> Optional[Receta]:
        return db.query(Receta).options(joinedload(Receta.detalles)).filter(Receta.id_receta == receta_id, Receta.anulado == False).first()

    def create(self, db: Session, receta: RecetaCreate) -> Receta:
        db_receta = Receta(
            id_producto=receta.id_producto,
            codigo_receta=receta.codigo_receta,
            nombre_receta=receta.nombre_receta,
            descripcion=receta.descripcion,
            rendimiento_producto_terminado=receta.rendimiento_producto_terminado,
            costo_estimado=receta.costo_estimado,
            version=receta.version,
            estado=receta.estado
        )
        db.add(db_receta)
        db.flush()  # Para obtener el id de la receta creada

        for detalle_data in receta.detalles:
            db_detalle = RecetaDetalle(**detalle_data.model_dump(), id_receta=db_receta.id_receta)
            db.add(db_detalle)

        db.commit()
        db.refresh(db_receta)
        return db_receta

    def update(self, db: Session, receta_id: int, receta: RecetaUpdate) -> Optional[Receta]:
        db_receta = self.get_by_id(db, receta_id)
        if db_receta:
            update_data = receta.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                if key != "detalles":
                    setattr(db_receta, key, value)

            if "detalles" in update_data and update_data["detalles"] is not None:
                # Eliminar detalles existentes
                db.query(RecetaDetalle).filter(RecetaDetalle.id_receta == receta_id).delete()
                # Agregar nuevos detalles
                for detalle_data in receta.detalles:
                    db_detalle = RecetaDetalle(**detalle_data.model_dump(), id_receta=receta_id)
                    db.add(db_detalle)

            db.commit()
            db.refresh(db_receta)
        return db_receta

    def delete(self, db: Session, receta_id: int) -> bool:
        db_receta = self.get_by_id(db, receta_id)
        if db_receta:
            db_receta.anulado = True
            db.commit()
            return True
        return False
