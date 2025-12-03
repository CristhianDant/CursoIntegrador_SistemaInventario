"""Crear tabla historial_backup

Revision ID: f837844d0006
Revises: f837844d0005
Create Date: 2025-12-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f837844d0006'
down_revision: Union[str, None] = 'f837844d0005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crear tabla historial_backup para registro de backups del sistema."""
    op.create_table(
        'historial_backup',
        # Columna primaria
        sa.Column('id_backup', sa.BigInteger(), autoincrement=True, nullable=False),
        
        # Tipo de backup
        sa.Column('tipo', sa.String(length=20), nullable=False, comment='COMPLETO o DIFERENCIAL'),
        
        # Información del archivo
        sa.Column('nombre_archivo', sa.String(length=255), nullable=False),
        sa.Column('ruta_archivo', sa.Text(), nullable=False),
        sa.Column('tamanio_bytes', sa.BigInteger(), nullable=True, comment='Tamaño en bytes'),
        sa.Column('tamanio_legible', sa.String(length=50), nullable=True, comment='Ej: 15.5 MB'),
        
        # Estado
        sa.Column('estado', sa.String(length=20), nullable=False, server_default='COMPLETADO',
                  comment='COMPLETADO, ERROR, EN_PROCESO'),
        sa.Column('mensaje_error', sa.Text(), nullable=True),
        
        # Métricas
        sa.Column('duracion_segundos', sa.Float(), nullable=True),
        sa.Column('tablas_respaldadas', sa.BigInteger(), nullable=True),
        sa.Column('registros_totales', sa.BigInteger(), nullable=True),
        
        # Hash para verificación
        sa.Column('hash_md5', sa.String(length=32), nullable=True),
        
        # Referencia al backup base (para diferenciales)
        sa.Column('id_backup_base', sa.BigInteger(), nullable=True,
                  comment='FK al backup completo base para diferenciales'),
        
        # Auditoría
        sa.Column('fecha_creacion', sa.TIMESTAMP(timezone=True), 
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('fecha_eliminacion', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('eliminado', sa.Boolean(), server_default='false', nullable=False),
        
        # Ejecutado por
        sa.Column('ejecutado_por', sa.String(length=100), nullable=True,
                  comment='SCHEDULER, MANUAL, o nombre de usuario'),
        
        # Primary Key
        sa.PrimaryKeyConstraint('id_backup')
    )
    
    # Crear índices
    op.create_index('ix_historial_backup_tipo', 'historial_backup', ['tipo'])
    op.create_index('ix_historial_backup_estado', 'historial_backup', ['estado'])
    op.create_index('ix_historial_backup_fecha_creacion', 'historial_backup', ['fecha_creacion'])
    op.create_index('ix_historial_backup_eliminado', 'historial_backup', ['eliminado'])
    
    # Agregar tipo BACKUP a la tabla de notificaciones (si no existe)
    # Las notificaciones de backup se registran con tipo='BACKUP'


def downgrade() -> None:
    """Eliminar tabla historial_backup."""
    op.drop_index('ix_historial_backup_eliminado', table_name='historial_backup')
    op.drop_index('ix_historial_backup_fecha_creacion', table_name='historial_backup')
    op.drop_index('ix_historial_backup_estado', table_name='historial_backup')
    op.drop_index('ix_historial_backup_tipo', table_name='historial_backup')
    op.drop_table('historial_backup')
