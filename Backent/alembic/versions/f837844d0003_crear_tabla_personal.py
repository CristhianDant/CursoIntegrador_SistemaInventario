"""crear tabla personal

Revision ID: f837844d0003
Revises: f837844d0002
Create Date: 2025-11-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f837844d0003'
down_revision: Union[str, Sequence[str], None] = 'f837844d0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - crear tabla personal."""
    op.create_table('personal',
        sa.Column('id_personal', sa.BIGINT, primary_key=True, autoincrement=True),
        sa.Column('id_usuario', sa.BIGINT, sa.ForeignKey('usuario.id_user', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('nombre_completo', sa.VARCHAR(255), nullable=False),
        sa.Column('direccion', sa.TEXT, nullable=True),
        sa.Column('referencia', sa.TEXT, nullable=True),
        sa.Column('dni', sa.VARCHAR(20), unique=True, nullable=False),
        sa.Column('area', sa.VARCHAR(50), nullable=True),
        sa.Column('salario', sa.DECIMAL(12, 2), nullable=False, server_default='0'),
        sa.Column('anulado', sa.BOOLEAN, nullable=False, server_default='false'),
        sa.Column('fecha_registro', sa.TIMESTAMP, nullable=False, server_default=sa.func.now())
    )


def downgrade() -> None:
    """Downgrade schema - eliminar tabla personal."""
    op.drop_table('personal')
