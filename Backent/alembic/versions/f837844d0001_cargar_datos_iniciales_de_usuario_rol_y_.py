"""Cargar datos iniciales de usuario, rol y permisos

Revision ID: f837844d0001
Revises: 82a795feb898
Create Date: 2025-11-17 09:33:38.257004

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision: str = 'f837844d0001'
down_revision: Union[str, Sequence[str], None] = '82a795feb898'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Definición de las tablas para la inserción de datos
roles_table = sa.table('roles',
    sa.column('id_rol', sa.Integer),
    sa.column('nombre_rol', sa.String)
)

permisos_table = sa.table('permisos',
    sa.column('id_permiso', sa.Integer),
    sa.column('accion', sa.String),
    sa.column('modulo', sa.String)
)

roles_permisos_table = sa.table('roles_permisos',
    sa.column('id_rol', sa.Integer),
    sa.column('id_permiso', sa.Integer)
)

usuarios_table = sa.table('usuario',
    sa.column('id_user', sa.Integer),
    sa.column('nombre', sa.String),
    sa.column('apellidos', sa.String),
    sa.column('email', sa.String),
    sa.column('password', sa.String),
    sa.column('fecha_registro', sa.DateTime),
    sa.column('ultimo_acceso', sa.DateTime),
    sa.column('anulado', sa.Boolean)
)

usuario_roles_table = sa.table('usuario_roles',
    sa.column('id_user', sa.Integer),
    sa.column('id_rol', sa.Integer)
)

modulos = [
    "USUARIOS", "ROLES", "PROVEEDORES", "INSUMOS", "PRODUCTOS",
    "RECETAS", "COMPRAS", "INVENTARIO", "PRODUCCION", "MERMA",
    "REPORTES", "CONFIGURACION"
]

def upgrade() -> None:
    """Upgrade schema."""
    # Insertar rol de Administrador
    op.bulk_insert(roles_table, [{'id_rol': 1, 'nombre_rol': 'Administrador'}])

    # Insertar permisos
    permisos_data = []
    permiso_id = 1
    for modulo in modulos:
        permisos_data.append({'id_permiso': permiso_id, 'accion': 'Leer', 'modulo': modulo})
        permiso_id += 1
        permisos_data.append({'id_permiso': permiso_id, 'accion': 'Escribir', 'modulo': modulo})
        permiso_id += 1
    op.bulk_insert(permisos_table, permisos_data)

    # Asignar todos los permisos al rol de Administrador
    roles_permisos_data = [{'id_rol': 1, 'id_permiso': i} for i in range(1, permiso_id)]
    op.bulk_insert(roles_permisos_table, roles_permisos_data)

    # Insertar usuario Administrador
    op.bulk_insert(usuarios_table, [
        {
            'id_user': 1,
            'nombre': 'Admin',
            'apellidos': 'Admin',
            'email': 'admin@email.com',
            'password': '$pbkdf2-sha256$29000$VWqNMYbwnnNOiZESAiBE6A$d2qR2gSnNeOmMgx7uivQ3n54mjgqMf46rKufW0wEASw',
            'fecha_registro': datetime.now(timezone.utc),
            'ultimo_acceso': None,
            'anulado': False
        }
    ])

    # Asignar rol de Administrador al usuario Administrador
    op.bulk_insert(usuario_roles_table, [{'id_user': 1, 'id_rol': 1}])


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(usuario_roles_table.delete().where(usuario_roles_table.c.id_user == 1))
    op.execute(usuarios_table.delete().where(usuarios_table.c.id_user == 1))
    op.execute(roles_permisos_table.delete().where(roles_permisos_table.c.id_rol == 1))
    op.execute(permisos_table.delete())
    op.execute(roles_table.delete().where(roles_table.c.id_rol == 1))
