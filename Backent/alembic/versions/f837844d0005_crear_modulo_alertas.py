"""crear modulo alertas - tabla notificaciones y campo JSONB en empresa

Revision ID: f837844d0005
Revises: da969acf1e8c
Create Date: 2025-12-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'f837844d0005'
down_revision: Union[str, Sequence[str], None] = 'da969acf1e8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Configuración por defecto para alertas
DEFAULT_CONFIGURACION_ALERTAS = {
    "dias_verde": 15,
    "dias_amarillo": 7,
    "dias_rojo": 3,
    "hora_job": "06:00",
    "email_alertas": None
}


def upgrade() -> None:
    """
    Upgrade schema:
    1. Limpiar tipos ENUM anteriores si existen (de migraciones fallidas)
    2. Agregar campo configuracion_alertas (JSONB) a tabla empresa
    3. Crear tabla notificaciones (usando VARCHAR en lugar de ENUM de BD)
    """
    
    # 0. Limpiar objetos de intentos anteriores (si existen)
    op.execute("DROP TABLE IF EXISTS notificaciones CASCADE")
    op.execute("DROP TYPE IF EXISTS tipoalerta CASCADE")
    op.execute("DROP TYPE IF EXISTS semaforoestado CASCADE")
    
    # 1. Agregar campo JSONB a tabla empresa (si no existe)
    # Primero verificamos si ya existe la columna
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'empresa' AND column_name = 'configuracion_alertas'
            ) THEN
                ALTER TABLE empresa ADD COLUMN configuracion_alertas JSONB;
            END IF;
        END $$;
    """)
    
    # Actualizar registros existentes con valores por defecto
    op.execute(
        """
        UPDATE empresa 
        SET configuracion_alertas = '{"dias_verde": 15, "dias_amarillo": 7, "dias_rojo": 3, "hora_job": "06:00", "email_alertas": null}'::jsonb
        WHERE configuracion_alertas IS NULL
        """
    )
    
    # 2. Crear tabla notificaciones (usando VARCHAR para tipos, no ENUM de BD)
    op.create_table(
        'notificaciones',
        sa.Column('id_notificacion', sa.BIGINT, primary_key=True, autoincrement=True),
        
        # Tipo y contenido (VARCHAR en lugar de ENUM de BD)
        sa.Column('tipo', sa.VARCHAR(50), nullable=False),  # STOCK_CRITICO, VENCIMIENTO_PROXIMO, USAR_HOY, VENCIDO
        sa.Column('titulo', sa.VARCHAR(200), nullable=False),
        sa.Column('mensaje', sa.TEXT, nullable=False),
        
        # Referencias opcionales
        sa.Column('id_insumo', sa.BIGINT, sa.ForeignKey('insumo.id_insumo', ondelete='SET NULL'), nullable=True),
        sa.Column('id_ingreso_detalle', sa.BIGINT, sa.ForeignKey('ingresos_insumos_detalle.id_ingreso_detalle', ondelete='SET NULL'), nullable=True),
        
        # Metadatos adicionales (VARCHAR en lugar de ENUM de BD)
        sa.Column('semaforo', sa.VARCHAR(20), nullable=True),  # VERDE, AMARILLO, ROJO
        sa.Column('dias_restantes', sa.BIGINT, nullable=True),
        sa.Column('cantidad_afectada', sa.VARCHAR(50), nullable=True),
        
        # Estado
        sa.Column('leida', sa.BOOLEAN, nullable=False, server_default='false'),
        sa.Column('activa', sa.BOOLEAN, nullable=False, server_default='true'),
        
        # Auditoría
        sa.Column('fecha_creacion', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('fecha_lectura', sa.TIMESTAMP(timezone=True), nullable=True)
    )
    
    # 3. Crear índices para optimizar consultas
    op.create_index('idx_notificaciones_tipo', 'notificaciones', ['tipo'])
    op.create_index('idx_notificaciones_insumo', 'notificaciones', ['id_insumo'])
    op.create_index('idx_notificaciones_activa', 'notificaciones', ['activa'])
    op.create_index('idx_notificaciones_leida', 'notificaciones', ['leida'])
    op.create_index('idx_notificaciones_fecha', 'notificaciones', ['fecha_creacion'])
    
    # Índice compuesto para consultas frecuentes
    op.create_index(
        'idx_notificaciones_activa_leida',
        'notificaciones',
        ['activa', 'leida'],
        postgresql_where=sa.text("activa = true")
    )


def downgrade() -> None:
    """
    Downgrade schema:
    1. Eliminar tabla notificaciones
    2. Eliminar campo configuracion_alertas de empresa
    """
    
    # 1. Eliminar índices y tabla
    op.drop_index('idx_notificaciones_activa_leida', table_name='notificaciones')
    op.drop_index('idx_notificaciones_fecha', table_name='notificaciones')
    op.drop_index('idx_notificaciones_leida', table_name='notificaciones')
    op.drop_index('idx_notificaciones_activa', table_name='notificaciones')
    op.drop_index('idx_notificaciones_insumo', table_name='notificaciones')
    op.drop_index('idx_notificaciones_tipo', table_name='notificaciones')
    op.drop_table('notificaciones')
    
    # 2. Eliminar columna de empresa
    op.drop_column('empresa', 'configuracion_alertas')
