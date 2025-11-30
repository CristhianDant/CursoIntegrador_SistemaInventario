"""crear tablas ventas y venta_detalles

Revision ID: 6b63e6c03e7f
Revises: f837844d0004
Create Date: 2025-11-29 04:55:44.629356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b63e6c03e7f'
down_revision: Union[str, Sequence[str], None] = 'f837844d0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - crear tablas ventas y venta_detalles."""
    # Crear tabla ventas
    op.create_table('ventas',
        sa.Column('id_venta', sa.BIGINT, primary_key=True, autoincrement=True),
        sa.Column('numero_venta', sa.VARCHAR(50), unique=True, nullable=False),
        sa.Column('fecha_venta', sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
        sa.Column('total', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('metodo_pago', sa.VARCHAR(20), nullable=False),
        sa.Column('id_user', sa.BIGINT, sa.ForeignKey('usuario.id_user', ondelete='RESTRICT'), nullable=False),
        sa.Column('observaciones', sa.TEXT, nullable=True),
        sa.Column('anulado', sa.BOOLEAN, nullable=False, server_default='false')
    )
    
    # Crear índices para tabla ventas
    op.create_index('idx_venta_fecha', 'ventas', ['fecha_venta'])
    op.create_index('idx_venta_usuario', 'ventas', ['id_user'])
    
    # Crear tabla venta_detalles
    op.create_table('venta_detalles',
        sa.Column('id_detalle', sa.BIGINT, primary_key=True, autoincrement=True),
        sa.Column('id_venta', sa.BIGINT, sa.ForeignKey('ventas.id_venta', ondelete='CASCADE'), nullable=False),
        sa.Column('id_producto', sa.BIGINT, sa.ForeignKey('productos_terminados.id_producto', ondelete='RESTRICT'), nullable=False),
        sa.Column('cantidad', sa.DECIMAL(12, 4), nullable=False),
        sa.Column('precio_unitario', sa.DECIMAL(12, 2), nullable=False),
        sa.Column('descuento_porcentaje', sa.DECIMAL(5, 2), nullable=False, server_default='0'),
        sa.Column('subtotal', sa.DECIMAL(12, 2), nullable=False)
    )
    
    # Crear índices para tabla venta_detalles
    op.create_index('idx_detalle_venta', 'venta_detalles', ['id_venta'])
    op.create_index('idx_detalle_producto', 'venta_detalles', ['id_producto'])


def downgrade() -> None:
    """Downgrade schema - eliminar tablas ventas y venta_detalles."""
    # Eliminar índices de venta_detalles
    op.drop_index('idx_detalle_producto', table_name='venta_detalles')
    op.drop_index('idx_detalle_venta', table_name='venta_detalles')
    
    # Eliminar tabla venta_detalles
    op.drop_table('venta_detalles')
    
    # Eliminar índices de ventas
    op.drop_index('idx_venta_usuario', table_name='ventas')
    op.drop_index('idx_venta_fecha', table_name='ventas')
    
    # Eliminar tabla ventas
    op.drop_table('ventas')
