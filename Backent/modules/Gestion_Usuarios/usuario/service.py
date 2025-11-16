from sqlalchemy.orm import Session
from typing import List, Optional

from .repository import UsuarioRepository
from .schemas import Usuario, UsuarioCreate, UsuarioUpdate
from .service_interface import UsuarioServiceInterface
from security.password_utils import get_password_hash

class UsuarioService(UsuarioServiceInterface):
    def __init__(self):
        self.repository = UsuarioRepository()

    def get_all(self, db: Session) -> List[Usuario]:
        return self.repository.get_all(db)

    def get_by_id(self, db: Session, user_id: int) -> Optional[Usuario]:
        return self.repository.get_by_id(db, user_id)

    def get_by_email(self, db: Session, email: str) -> Optional[Usuario]:
        return self.repository.get_by_email(db, email)

    def create(self, db: Session, user: UsuarioCreate) -> Usuario:
        # Verficar si el correo electronico ya existe
        email_user = str(user.email)
        existing_user = self.repository.get_by_email(db, email_user)
        if existing_user:
            raise ValueError("El correo electrónico ya está registrado")
        # Hash de la contraseña antes de guardar
        hashed_password = get_password_hash(user.password)
        user.password = hashed_password
        # Comverir el objeto Pydantic a diccionario
        user_data = user.model_dump()
        try:
            new_user = self.repository.create(db, user_data)
            db.commit()
            db.refresh(new_user)
            return new_user
        except Exception as e:
            db.rollback()
            raise e from e

    def update(self, db: Session, user_id: int, user_update: UsuarioUpdate) -> Optional[Usuario]:
        if user_update.password:
            user_update.password = get_password_hash(user_update.password)
        return self.repository.update(db, user_id, user_update)

    def delete(self, db: Session, user_id: int) -> bool:
        return self.repository.delete(db, user_id)

    def update_last_access(self, db: Session, user_id: int) -> Optional[Usuario]:
        return self.repository.update_last_access(db, user_id)

