"""crear tabla produccion

Revision ID: f837844d0004
Revises: f837844d0003
Create Date: 2025-11-29 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f837844d0004'
down_revision: Union[str, Sequence[str], None] = 'f837844d0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - crear tabla produccion."""
    op.create_table('produccion',
        sa.Column('id_produccion', sa.BIGINT, primary_key=True, autoincrement=True),
        sa.Column('numero_produccion', sa.VARCHAR(50), unique=True, nullable=False),
        sa.Column('id_receta', sa.BIGINT, sa.ForeignKey('recetas.id_receta', ondelete='RESTRICT'), nullable=False),
        sa.Column('cantidad_batch', sa.DECIMAL(12, 4), nullable=False),
        sa.Column('fecha_produccion', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
        sa.Column('id_user', sa.BIGINT, sa.ForeignKey('usuario.id_user', ondelete='RESTRICT'), nullable=False),
        sa.Column('observaciones', sa.TEXT, nullable=True),
        sa.Column('anulado', sa.BOOLEAN, nullable=False, server_default='false')
    )
    
    # Crear índice para búsquedas frecuentes
    op.create_index('idx_produccion_fecha', 'produccion', ['fecha_produccion'])
    op.create_index('idx_produccion_receta', 'produccion', ['id_receta'])


def downgrade() -> None:
    """Downgrade schema - eliminar tabla produccion."""
    op.drop_index('idx_produccion_receta', table_name='produccion')
    op.drop_index('idx_produccion_fecha', table_name='produccion')
    op.drop_table('produccion')
