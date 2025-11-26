from sqlalchemy.orm import Session
from typing import List, Optional

from .repository import UsuarioRepository
from .schemas import Usuario, UsuarioCreate, UsuarioUpdate
from .service_interface import UsuarioServiceInterface
from security.password_utils import get_password_hash
from modules.Gestion_Usuarios.roles.repository import RolRepository
from modules.Gestion_Usuarios.personal.repository import PersonalRepository

class UsuarioService(UsuarioServiceInterface):
    def __init__(self):
        self.repository = UsuarioRepository()
        self.rol_repository = RolRepository()
        self.personal_repository = PersonalRepository()

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

        # Validar que el DNI no exista
        existing_dni = self.personal_repository.get_by_dni(db, user.personal.dni)
        if existing_dni:
            raise ValueError("El DNI ya está registrado")

        # Validar que todos los roles existan
        if user.lista_roles:
            for rol_id in user.lista_roles:
                rol = self.rol_repository.get_by_id(db, rol_id)
                if not rol:
                    raise ValueError(f"El rol con ID {rol_id} no existe.")

        # Hash de la contraseña antes de guardar
        hashed_password = get_password_hash(user.password)
        user.password = hashed_password

        try:
            # Crear usuario
            db_user = self.repository.create(db, user)
            
            # Crear personal asociado
            personal_data = user.personal.model_dump()
            personal_data['id_usuario'] = db_user.id_user
            db_personal = self.personal_repository.create(db, personal_data)
            
            # Asignar personal al usuario para la relación
            db_user.personal = db_personal
            
            # Guardar roles
            if user.lista_roles:
                self.repository.save_roles_user(db, db_user, user.lista_roles)
            
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            print(e)
            db.rollback()
            raise e

    def update(self, db: Session, user_id: int, user_update: UsuarioUpdate) -> Optional[Usuario]:
        db_user = self.repository.get_by_id(db, user_id)
        if not db_user:
            raise ValueError("El usuario no existe.")

        if user_update.lista_roles is not None:
            for rol_id in user_update.lista_roles:
                rol = self.rol_repository.get_by_id(db, rol_id)
                if not rol:
                    db.rollback()
                    raise ValueError(f"El rol con ID {rol_id} no existe.")

        if user_update.password:
            user_update.password = get_password_hash(user_update.password)

        self.repository.update(db, user_id, user_update)

        if user_update.lista_roles is not None:
            self.repository.clear_roles_from_user(db, db_user)
            if user_update.lista_roles:
                self.repository.save_roles_user(db, db_user, user_update.lista_roles)

        # Actualizar datos de personal si se proporcionan
        if user_update.personal is not None:
            personal = self.personal_repository.get_by_usuario_id(db, user_id)
            if personal:
                # Validar DNI único si se está cambiando
                if user_update.personal.dni is not None:
                    existing_dni = self.personal_repository.get_by_dni(db, user_update.personal.dni)
                    if existing_dni and existing_dni.id_personal != personal.id_personal:
                        db.rollback()
                        raise ValueError("El DNI ya está registrado por otro personal")
                self.personal_repository.update(db, personal.id_personal, user_update.personal)

        # Sincronizar estado anulado con personal
        if user_update.anulado is not None:
            personal = self.personal_repository.get_by_usuario_id(db, user_id)
            if personal:
                self.personal_repository.update_estado(db, personal.id_personal, user_update.anulado)

        db.commit()
        db.refresh(db_user)
        return db_user

    def delete(self, db: Session, user_id: int) -> bool:
        # Sincronizar estado anulado con personal
        personal = self.personal_repository.get_by_usuario_id(db, user_id)
        if personal:
            self.personal_repository.update_estado(db, personal.id_personal, True)
        return self.repository.delete(db, user_id)

    def update_last_access(self, db: Session, user_id: int) -> Optional[Usuario]:
        return self.repository.update_last_access(db, user_id)

