from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import date
from .model import Promocion, PromocionCombo, EstadoPromocion, TipoPromocion
from .repository_interface import PromocionRepositoryInterface


class PromocionRepository(PromocionRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, include_anulados: bool = False) -> List[Promocion]:
        query = self.db.query(Promocion).options(
            joinedload(Promocion.producto),
            joinedload(Promocion.productos_combo)
        )
        if not include_anulados:
            query = query.filter(Promocion.anulado == False)
        return query.order_by(Promocion.fecha_creacion.desc()).all()

    def get_by_id(self, promocion_id: int) -> Optional[Promocion]:
        return self.db.query(Promocion).options(
            joinedload(Promocion.producto),
            joinedload(Promocion.productos_combo)
        ).filter(Promocion.id_promocion == promocion_id).first()

    def get_by_codigo(self, codigo: str) -> Optional[Promocion]:
        return self.db.query(Promocion).filter(Promocion.codigo_promocion == codigo).first()

    def get_activas(self) -> List[Promocion]:
        today = date.today()
        return self.db.query(Promocion).options(
            joinedload(Promocion.producto),
            joinedload(Promocion.productos_combo)
        ).filter(
            and_(
                Promocion.estado == EstadoPromocion.ACTIVA,
                Promocion.fecha_inicio <= today,
                Promocion.fecha_fin >= today,
                Promocion.anulado == False
            )
        ).all()

    def get_sugeridas(self) -> List[Promocion]:
        return self.db.query(Promocion).options(
            joinedload(Promocion.producto),
            joinedload(Promocion.productos_combo)
        ).filter(
            and_(
                Promocion.estado == EstadoPromocion.SUGERIDA,
                Promocion.anulado == False
            )
        ).order_by(Promocion.dias_hasta_vencimiento.asc()).all()

    def get_by_producto(self, producto_id: int) -> List[Promocion]:
        return self.db.query(Promocion).options(
            joinedload(Promocion.producto),
            joinedload(Promocion.productos_combo)
        ).filter(
            and_(
                Promocion.id_producto == producto_id,
                Promocion.anulado == False
            )
        ).all()

    def get_by_estado(self, estado: EstadoPromocion) -> List[Promocion]:
        return self.db.query(Promocion).options(
            joinedload(Promocion.producto),
            joinedload(Promocion.productos_combo)
        ).filter(
            and_(
                Promocion.estado == estado,
                Promocion.anulado == False
            )
        ).all()

    def create(self, promocion_data: dict, productos_combo: List[dict] = None) -> Promocion:
        promocion = Promocion(**promocion_data)
        self.db.add(promocion)
        self.db.flush()  # Para obtener el ID

        if productos_combo:
            for pc in productos_combo:
                combo = PromocionCombo(
                    id_promocion=promocion.id_promocion,
                    id_producto=pc['id_producto'],
                    cantidad=pc.get('cantidad', 1),
                    descuento_individual=pc.get('descuento_individual', 0)
                )
                self.db.add(combo)

        self.db.commit()
        self.db.refresh(promocion)
        return promocion

    def update(self, promocion_id: int, update_data: dict, productos_combo: List[dict] = None) -> Optional[Promocion]:
        promocion = self.get_by_id(promocion_id)
        if not promocion:
            return None

        for key, value in update_data.items():
            if hasattr(promocion, key) and value is not None:
                setattr(promocion, key, value)

        # Actualizar productos combo si se proporcionan
        if productos_combo is not None:
            # Eliminar combos existentes
            self.db.query(PromocionCombo).filter(
                PromocionCombo.id_promocion == promocion_id
            ).delete()
            
            # Agregar nuevos
            for pc in productos_combo:
                combo = PromocionCombo(
                    id_promocion=promocion_id,
                    id_producto=pc['id_producto'],
                    cantidad=pc.get('cantidad', 1),
                    descuento_individual=pc.get('descuento_individual', 0)
                )
                self.db.add(combo)

        self.db.commit()
        self.db.refresh(promocion)
        return promocion

    def cambiar_estado(self, promocion_id: int, nuevo_estado: EstadoPromocion) -> Optional[Promocion]:
        promocion = self.get_by_id(promocion_id)
        if promocion:
            promocion.estado = nuevo_estado
            self.db.commit()
            self.db.refresh(promocion)
        return promocion

    def incrementar_uso(self, promocion_id: int) -> Optional[Promocion]:
        promocion = self.get_by_id(promocion_id)
        if promocion:
            promocion.veces_aplicada += 1
            self.db.commit()
            self.db.refresh(promocion)
        return promocion

    def delete(self, promocion_id: int) -> bool:
        promocion = self.get_by_id(promocion_id)
        if promocion:
            promocion.anulado = True
            self.db.commit()
            return True
        return False

    def delete_sugerencias_producto(self, producto_id: int) -> int:
        """Elimina todas las sugerencias automáticas de un producto"""
        result = self.db.query(Promocion).filter(
            and_(
                Promocion.id_producto == producto_id,
                Promocion.estado == EstadoPromocion.SUGERIDA,
                Promocion.creado_automaticamente == True
            )
        ).update({Promocion.anulado: True})
        self.db.commit()
        return result

    def get_next_codigo(self) -> str:
        """Genera el siguiente código de promoción"""
        last = self.db.query(Promocion).order_by(Promocion.id_promocion.desc()).first()
        next_num = (last.id_promocion + 1) if last else 1
        return f"PROMO-{next_num:06d}"

    def existe_sugerencia_similar(self, producto_id: int, tipo: TipoPromocion) -> bool:
        """Verifica si ya existe una sugerencia similar activa"""
        return self.db.query(Promocion).filter(
            and_(
                Promocion.id_producto == producto_id,
                Promocion.tipo_promocion == tipo,
                Promocion.estado == EstadoPromocion.SUGERIDA,
                Promocion.anulado == False
            )
        ).first() is not None
