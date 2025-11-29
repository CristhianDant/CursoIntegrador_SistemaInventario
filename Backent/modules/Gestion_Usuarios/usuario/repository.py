from sqlalchemy.orm import Session , joinedload
from typing import List, Optional
from datetime import datetime, timezone

from .model import Usuario
from .schemas import UsuarioCreate, UsuarioUpdate
from .repository_interface import UsuarioRepositoryInterfaz
from modules.Gestion_Usuarios.roles.model import Rol

class UsuarioRepository(UsuarioRepositoryInterfaz):
    def get_all(self, db: Session) -> List[Usuario]:
        return db.query(Usuario).options(
            joinedload(Usuario.roles),
            joinedload(Usuario.personal)
        ).filter(Usuario.anulado == False).all()

    def get_by_id(self, db: Session, user_id: int) -> Optional[Usuario]:
        return db.query(Usuario).options(
            joinedload(Usuario.roles),
            joinedload(Usuario.personal)
        ).filter(Usuario.id_user == user_id, Usuario.anulado == False).first()


    def get_by_email(self, db: Session, email: str, solo_activos: bool = True) -> Optional[Usuario]:
        query = db.query(Usuario).options(
            joinedload(Usuario.roles),
            joinedload(Usuario.personal)
        ).filter(Usuario.email == email)
        
        if solo_activos:
            query = query.filter(Usuario.anulado == False)
        
        return query.first()

    def create(self, db: Session, user: UsuarioCreate) -> Usuario:
        user_data = user.model_dump(exclude={'lista_roles', 'personal'})
        db_user = Usuario(**user_data)
        db.add(db_user)
        db.flush()
        db.refresh(db_user)
        return db_user

    def update(self, db: Session, user_id: int, user_update: UsuarioUpdate) -> Optional[Usuario]:
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True, exclude={'lista_roles', 'personal'})
        for key, value in update_data.items():
            setattr(db_user, key, value)

        db.flush()
        db.refresh(db_user)
        return db_user

    def delete(self, db: Session, user_id: int) -> bool:
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.anulado = True
            db.commit()
            return True
        return False

    def clear_roles_from_user(self, db: Session, db_user: Usuario):
        db_user.roles.clear()
        db.flush()

    def save_roles_user(self, db: Session, db_user: Usuario, roles_ids: List[int]):
        if roles_ids:
            roles = db.query(Rol).filter(Rol.id_rol.in_(roles_ids)).all()
            db_user.roles = roles
            db.flush()

    def update_last_access(self, db: Session, user_id: int) -> Optional[Usuario]:
        db_user = self.get_by_id(db, user_id)
        if db_user:
            db_user.ultimo_acceso = datetime.now(timezone.utc)
            db.commit()
            db.refresh(db_user)
        return db_user
