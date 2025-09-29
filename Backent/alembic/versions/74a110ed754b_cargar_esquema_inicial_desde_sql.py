"""Cargar esquema inicial desde SQL

Revision ID: 74a110ed754b
Revises: 
Create Date: 2025-09-28 15:17:25.988570

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = '74a110ed754b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Get the directory of the current script
    sql_file_path = os.path.join(os.path.dirname(__file__), '../../shemas.sql')
    with open(sql_file_path) as f:
        op.execute(f.read())


def downgrade() -> None:
    """Downgrade schema."""
    # This is a basic downgrade, you might need to adjust it depending on your needs
    # It will drop all tables, which might not be ideal in all scenarios
    op.execute("DROP TABLE IF EXISTS calidad_desperdicio_merma, movimiento_productos_terminados, movimiento_insumos, productos_terminados, recetas_detalle, recetas, ingresos_productos_detalle, ingresos_productos, orden_de_compra_detalle, orden_de_compra, costo_insumos, insumo, proveedores, usuario_permisos, permisos, usuario, empresa CASCADE;")
