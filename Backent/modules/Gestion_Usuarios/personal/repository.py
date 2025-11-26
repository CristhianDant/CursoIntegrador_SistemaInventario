from sqlalchemy.orm import Session
from typing import Optional

from .model import Personal
from .schemas import PersonalUpdate
from .repository_interface import PersonalRepositoryInterface


class PersonalRepository(PersonalRepositoryInterface):
    def get_by_id(self, db: Session, personal_id: int) -> Optional[Personal]:
        return db.query(Personal).filter(
            Personal.id_personal == personal_id,
            Personal.anulado == False
        ).first()

    def get_by_usuario_id(self, db: Session, usuario_id: int) -> Optional[Personal]:
        return db.query(Personal).filter(
            Personal.id_usuario == usuario_id
        ).first()

    def get_by_dni(self, db: Session, dni: str) -> Optional[Personal]:
        return db.query(Personal).filter(Personal.dni == dni).first()

    def create(self, db: Session, personal_data: dict) -> Personal:
        # Convertir enum a string si es necesario
        if 'area' in personal_data and personal_data['area'] is not None:
            if hasattr(personal_data['area'], 'value'):
                personal_data['area'] = personal_data['area'].value
        
        db_personal = Personal(**personal_data)
        db.add(db_personal)
        db.flush()
        db.refresh(db_personal)
        return db_personal

    def update(self, db: Session, personal_id: int, personal_update: PersonalUpdate) -> Optional[Personal]:
        db_personal = self.get_by_id(db, personal_id)
        if not db_personal:
            return None

        update_data = personal_update.model_dump(exclude_unset=True)
        
        # Convertir enum a string si es necesario
        if 'area' in update_data and update_data['area'] is not None:
            if hasattr(update_data['area'], 'value'):
                update_data['area'] = update_data['area'].value
        
        for key, value in update_data.items():
            setattr(db_personal, key, value)

        db.flush()
        db.refresh(db_personal)
        return db_personal

    def update_estado(self, db: Session, personal_id: int, anulado: bool) -> Optional[Personal]:
        db_personal = db.query(Personal).filter(Personal.id_personal == personal_id).first()
        if db_personal:
            db_personal.anulado = anulado
            db.flush()
            db.refresh(db_personal)
        return db_personal
