"""crear tabla cola_email

Revision ID: f837844d0004
Revises: f837844d0003
Create Date: 2025-11-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f837844d0004'
down_revision: Union[str, None] = 'f837844d0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('cola_email',
        sa.Column('id_email', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('destinatario', sa.VARCHAR(length=255), nullable=False),
        sa.Column('asunto', sa.VARCHAR(length=500), nullable=False),
        sa.Column('cuerpo_html', sa.TEXT(), nullable=False),
        sa.Column('estado', sa.VARCHAR(length=50), nullable=False, server_default='PENDIENTE'),
        sa.Column('intentos', sa.INTEGER(), nullable=False, server_default='0'),
        sa.Column('ultimo_error', sa.TEXT(), nullable=True),
        sa.Column('fecha_creacion', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('fecha_envio', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id_email')
    )
    
    # Crear índice para búsquedas por estado
    op.create_index('ix_cola_email_estado', 'cola_email', ['estado'])


def downgrade() -> None:
    op.drop_index('ix_cola_email_estado', table_name='cola_email')
    op.drop_table('cola_email')
