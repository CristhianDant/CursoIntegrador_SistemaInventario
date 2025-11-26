"""agregar cantidad_ordenada a ingresos_insumos_detalle

Revision ID: f837844d0002
Revises: f837844d0001
Create Date: 2025-11-26 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f837844d0002'
down_revision: Union[str, Sequence[str], None] = 'f837844d0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - agregar columna cantidad_ordenada."""
    # Agregar columna cantidad_ordenada a ingresos_insumos_detalle
    op.add_column('ingresos_insumos_detalle', sa.Column('cantidad_ordenada', sa.DECIMAL(12, 4), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema - eliminar columna cantidad_ordenada."""
    # Eliminar columna cantidad_ordenada
    op.drop_column('ingresos_insumos_detalle', 'cantidad_ordenada')
