from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from modules.usuario.model import Usuario
from modules.usuario.schemas import UsuarioCreate, UsuarioUpdate
from modules.usuario.repository_interface import UsuarioRepositoryInterfaz

class UsuarioRepository(UsuarioRepositoryInterfaz):
    def get_all(self, db: Session) -> List[Usuario]:
        return db.query(Usuario).filter(Usuario.anulado == False).all()

    def get_by_id(self, db: Session, user_id: int) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.id_user == user_id, Usuario.anulado == False).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.email == email, Usuario.anulado == False).first()

    def create(self, db: Session, user: dict) -> Usuario:
        db_user = Usuario(**user)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, user_id: int, user_update: UsuarioUpdate) -> Optional[Usuario]:
        db_user = self.get_by_id(db, user_id)
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_user, key, value)
            db.commit()
            db.refresh(db_user)
        return db_user

    def delete(self, db: Session, user_id: int) -> bool:
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.anulado = True
            db.commit()
            return True
        return False

    def update_last_access(self, db: Session, user_id: int) -> Optional[Usuario]:
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.ultimo_acceso = datetime.now(timezone.utc)
            db.commit()
            db.refresh(db_user)
        return db_user

