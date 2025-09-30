"""Cargar datos iniciales de permisos y usuario administrador

Revision ID: ee00bf3dd3b1
Revises: 74a110ed754b
Create Date: 2025-09-30 15:07:35.974775

"""
from typing import Sequence, Union
import os
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee00bf3dd3b1'
down_revision: Union[str, Sequence[str], None] = '74a110ed754b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Carga los datos iniciales desde data.sql."""
    # Obtiene la ruta absoluta al directorio actual del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construye la ruta al archivo data.sql (asumiendo que está en la raíz del proyecto)
    sql_file_path = os.path.join(script_dir, '..', '..', 'data.sql')

    with open(sql_file_path, 'r') as f:
        sql_commands = f.read().split(';')
        for command in sql_commands:
            if command.strip():
                op.execute(command)


def downgrade() -> None:
    """Elimina los datos iniciales cargados."""
    # Eliminar el usuario administrador
    op.execute("DELETE FROM usuario WHERE email = 'admin@email.com'")

    # Eliminar los permisos generales
    op.execute("DELETE FROM permisos WHERE accion = 'general'")
