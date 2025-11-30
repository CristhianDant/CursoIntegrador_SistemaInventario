"""crear tabla promociones

Revision ID: da969acf1e8c
Revises: c5bc7341cc8a
Create Date: 2025-11-30 10:18:08.497462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da969acf1e8c'
down_revision: Union[str, Sequence[str], None] = 'c5bc7341cc8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - crear tablas promociones y promociones_combo."""
    conn = op.get_bind()
    
    # Crear enums solo si no existen
    conn.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE tipopromocion AS ENUM ('DESCUENTO', 'COMBO', 'LIQUIDACION', 'TEMPORADA', 'LANZAMIENTO');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))
    
    conn.execute(sa.text("""
        DO $$ BEGIN
            CREATE TYPE estadopromocion AS ENUM ('SUGERIDA', 'ACTIVA', 'PAUSADA', 'FINALIZADA', 'CANCELADA');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """))

    # Crear tabla promociones
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS promociones (
            id_promocion BIGSERIAL PRIMARY KEY,
            codigo_promocion VARCHAR(50) UNIQUE NOT NULL,
            titulo VARCHAR(255) NOT NULL,
            descripcion TEXT,
            tipo_promocion tipopromocion NOT NULL DEFAULT 'DESCUENTO',
            estado estadopromocion NOT NULL DEFAULT 'SUGERIDA',
            id_producto BIGINT REFERENCES productos_terminados(id_producto),
            porcentaje_descuento NUMERIC(5,2) DEFAULT 0,
            precio_promocional NUMERIC(12,2),
            cantidad_minima INTEGER DEFAULT 1,
            fecha_inicio DATE NOT NULL,
            fecha_fin DATE NOT NULL,
            dias_hasta_vencimiento INTEGER,
            motivo TEXT,
            ahorro_potencial NUMERIC(12,2) DEFAULT 0,
            veces_aplicada INTEGER DEFAULT 0,
            fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
            fecha_modificacion TIMESTAMP NOT NULL DEFAULT NOW(),
            creado_automaticamente BOOLEAN DEFAULT FALSE,
            anulado BOOLEAN NOT NULL DEFAULT FALSE
        );
    """))

    # Crear tabla promociones_combo
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS promociones_combo (
            id BIGSERIAL PRIMARY KEY,
            id_promocion BIGINT NOT NULL REFERENCES promociones(id_promocion),
            id_producto BIGINT NOT NULL REFERENCES productos_terminados(id_producto),
            cantidad INTEGER DEFAULT 1,
            descuento_individual NUMERIC(5,2) DEFAULT 0
        );
    """))

    # Crear índices
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_promociones_estado ON promociones(estado);"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_promociones_tipo ON promociones(tipo_promocion);"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_promociones_producto ON promociones(id_producto);"))
    conn.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_promociones_fechas ON promociones(fecha_inicio, fecha_fin);"))


def downgrade() -> None:
    """Downgrade schema - eliminar tablas promociones."""
    conn = op.get_bind()
    
    # Eliminar índices
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_promociones_fechas;"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_promociones_producto;"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_promociones_tipo;"))
    conn.execute(sa.text("DROP INDEX IF EXISTS ix_promociones_estado;"))

    # Eliminar tablas
    conn.execute(sa.text("DROP TABLE IF EXISTS promociones_combo;"))
    conn.execute(sa.text("DROP TABLE IF EXISTS promociones;"))

    # Eliminar tipos enum
    conn.execute(sa.text("DROP TYPE IF EXISTS estadopromocion;"))
    conn.execute(sa.text("DROP TYPE IF EXISTS tipopromocion;"))
