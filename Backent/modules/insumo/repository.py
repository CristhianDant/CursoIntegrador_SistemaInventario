from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from modules.insumo.model import Insumo
from modules.insumo.schemas import InsumoCreate, InsumoUpdate
from modules.gestion_almacen_inusmos.ingresos_insumos.model import IngresoProducto, IngresoProductoDetalle
from .repository_interface import InsumoRepositoryInterface


class InsumoRepository(InsumoRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def get_insumo(self, insumo_id: int) -> Insumo | None:
        return self.db.query(Insumo).filter(Insumo.id_insumo == insumo_id).first()

    def get_inusmo_cod(self , codigo: str) -> Insumo | None:
        return self.db.query(Insumo).filter(Insumo.codigo == codigo).first()

    def get_insumos(self, skip: int = 0, limit: int = 100) -> list[Insumo]:
        return self.db.query(Insumo).filter(Insumo.anulado == False).offset(skip).limit(limit).all()

    def create_insumo(self, insumo: InsumoCreate) -> Insumo:
        db_insumo = Insumo(**insumo.model_dump())
        self.db.add(db_insumo)
        self.db.commit()
        self.db.refresh(db_insumo)
        return db_insumo

    def update_insumo(self, insumo_id: int, insumo: InsumoUpdate) -> Insumo | None:
        db_insumo = self.get_insumo(insumo_id)
        if db_insumo:
            update_data = insumo.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_insumo, key, value)
            self.db.commit()
            self.db.refresh(db_insumo)
        return db_insumo

    def delete_insumo(self, insumo_id: int) -> Insumo | None:
        db_insumo = self.db.query(Insumo).filter(Insumo.id_insumo == insumo_id).first()
        if db_insumo:
            db_insumo.anulado = True
            self.db.commit()
            self.db.refresh(db_insumo)
        return db_insumo

    def get_ultimos_precios(self) -> dict:
        """
        Obtiene el último precio de compra de cada insumo
        basándose en los ingresos de insumos más recientes.
        Retorna un diccionario {id_insumo: precio_unitario}
        """
        # Subconsulta para obtener el último ingreso por insumo
        subquery = (
            self.db.query(
                IngresoProductoDetalle.id_insumo,
                func.max(IngresoProducto.fecha_ingreso).label('ultima_fecha')
            )
            .join(IngresoProducto, IngresoProductoDetalle.id_ingreso == IngresoProducto.id_ingreso)
            .filter(IngresoProducto.anulado == False)
            .group_by(IngresoProductoDetalle.id_insumo)
            .subquery()
        )

        # Consulta principal para obtener el precio del último ingreso
        resultados = (
            self.db.query(
                IngresoProductoDetalle.id_insumo,
                IngresoProductoDetalle.precio_unitario
            )
            .join(IngresoProducto, IngresoProductoDetalle.id_ingreso == IngresoProducto.id_ingreso)
            .join(
                subquery,
                (IngresoProductoDetalle.id_insumo == subquery.c.id_insumo) &
                (IngresoProducto.fecha_ingreso == subquery.c.ultima_fecha)
            )
            .filter(IngresoProducto.anulado == False)
            .all()
        )

        return {r.id_insumo: float(r.precio_unitario) for r in resultados}
